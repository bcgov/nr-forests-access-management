<script setup lang="ts">
import router from '@/router';
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import { computed, onMounted, onUnmounted, ref } from 'vue';

import NotificationMessage from '@/components/common/NotificationMessage.vue';
import DashboardTitle from './DashboardTitle.vue';
import UserDataTable from './UserDataTable.vue';

import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
applicationsUserAdministers,
isApplicationSelected,
selectedApplication,
selectedApplicationDisplayText,
setSelectedApplication,
} from '@/store/ApplicationState';

import { useNotificationMessage } from '@/store/NotificationState';

import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';

const loading = ref<boolean>(false);
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const userRoleAssignments = ref<FamApplicationUserRoleAssignmentGet[]>();

onMounted(async () => {
    // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
    try {
        loading.value = true;
        applicationsUserAdministers.value = (
            await applicationsApi.getApplications()
        ).data;
        if (isApplicationSelected) {
            await getAppUserRoleAssignment();
        }
    } catch (error: any) {
        return Promise.reject(error);
    } finally {
        loading.value = false;
    }
});

onUnmounted(() => {
    useNotificationMessage.isNotificationVisible = false;
    useNotificationMessage.notificationMsg = '';
});

async function getAppUserRoleAssignment() {
    try {
        loading.value = true;
        if (!selectedApplication.value) return;
        const userRoleAssignmentList = (
            await applicationsApi.getFamApplicationUserRoleAssignment(
                selectedApplication.value.application_id
            )
        ).data;
        userRoleAssignments.value = userRoleAssignmentList.sort(
            (first, second) => {
                const nameCompare = first.user.user_name.localeCompare(
                    second.user.user_name
                );
                if (nameCompare != 0) return nameCompare;
                const roleCompare = first.role.role_name.localeCompare(
                    second.role.role_name
                );
                return roleCompare;
            }
        );
    } catch (error: unknown) {
        router.push('/dashboard');
        return Promise.reject(error);
    } finally {
        loading.value = false;
    }
}

const selectApplication = async (e: DropdownChangeEvent) => {
    try {
        setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
        if (applicationsUserAdministers) {
            await getAppUserRoleAssignment();
        }
    } catch (error: any) {
        return Promise.reject(error);
    }
};

const selectApplicationOptions = computed(() => {
    return applicationsUserAdministers.value;
});

async function deleteUserRoleAssignment(
    assignment: FamApplicationUserRoleAssignmentGet
) {
    try {
        await userRoleAssignmentApi.deleteUserRoleAssignment(
            assignment.user_role_xref_id
        );
        userRoleAssignments.value =
            userRoleAssignments.value!.filter((a) => {
                return (
                    a.user_role_xref_id !=
                    assignment.user_role_xref_id
                );
            });
        useNotificationMessage.notificationMsg = `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`;
        useNotificationMessage.isNotificationVisible = true;
    } catch (error) {
        return Promise.reject(error);
    }
}
</script>

<template>
    <DashboardTitle :isApplicationSelected="isApplicationSelected" />

    <div class="page-body">
        <div class="application-group">
            <label>Select an application you would like to grant access</label>
            <Dropdown
                v-model="selectedApplication"
                @change="selectApplication"
                :options="selectApplicationOptions"
                optionLabel="application_description"
                placeholder="Choose an option"
                class="application-dropdown"
            />
        </div>

        <NotificationMessage
            v-if="useNotificationMessage.isNotificationVisible"
            severity="success"
            :msgText="useNotificationMessage.notificationMsg"
        />

        <UserDataTable
            v-if="isApplicationSelected"
            :loading="loading"
            :userRoleAssignments="userRoleAssignments || []"
            :selectedApplicationDisplayText="selectedApplicationDisplayText"
            @deleteUserRoleAssignment="deleteUserRoleAssignment"
        />
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';

.application-dropdown {
    width: 19rem;
    padding: 0;
}

.application-group {
    display: grid;
}
</style>
