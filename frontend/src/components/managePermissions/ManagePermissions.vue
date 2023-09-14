<script setup lang="ts">
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import { computed, onMounted, onUnmounted, shallowRef } from 'vue';

import NotificationMessage from '@/components/common/NotificationMessage.vue';
import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/UserDataTable.vue';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    selectedApplicationDisplayText,
    setSelectedApplication,
} from '@/store/ApplicationState';
import LoadingState from '@/store/LoadingState';

import { useNotificationMessage } from '@/store/NotificationState';

import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';

const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>();

onMounted(async () => {
    // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
    applicationsUserAdministers.value = (
        await applicationsApi.getApplications()
        ).data;
        if (isApplicationSelected) {
            await getAppUserRoleAssignment();
        }
});

onUnmounted(() => {
    useNotificationMessage.isNotificationVisible = false;
    useNotificationMessage.notificationMsg = '';
});

async function getAppUserRoleAssignment() {
    if (!selectedApplication.value) return;

    const userRoleAssignmentList = (
        await applicationsApi.getFamApplicationUserRoleAssignment(
            selectedApplication.value.application_id
        )
    ).data;
    userRoleAssignments.value = userRoleAssignmentList.sort((first, second) => {
        const nameCompare = first.user.user_name.localeCompare(
            second.user.user_name
        );
        if (nameCompare != 0) return nameCompare;
        const roleCompare = first.role.role_name.localeCompare(
            second.role.role_name
        );
        return roleCompare;
    });
}

const selectApplication = async (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
    if (applicationsUserAdministers) {
        await getAppUserRoleAssignment();
    }
};

const selectApplicationOptions = computed(() => {
    return applicationsUserAdministers.value;
});

async function deleteUserRoleAssignment(
    assignment: FamApplicationUserRoleAssignmentGet
) {
    await userRoleAssignmentApi.deleteUserRoleAssignment(
        assignment.user_role_xref_id
    );
    userRoleAssignments.value = userRoleAssignments.value!.filter((a) => {
        return a.user_role_xref_id != assignment.user_role_xref_id;
    });
    useNotificationMessage.notificationMsg = `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`;
    useNotificationMessage.isNotificationVisible = true;
}
</script>

<template>
    <ManagePermissionsTitle :isApplicationSelected="isApplicationSelected" />

    <div class="page-body">
        <div class="application-group">
            <label>You are modifying access in this application:</label>
            <Dropdown
                v-model="selectedApplication"
                @change="selectApplication"
                :options="selectApplicationOptions"
                optionLabel="application_description"
                placeholder="Choose or enter an application to manage permissions"
                class="application-dropdown"
            />
        </div>

        <NotificationMessage
            v-if="useNotificationMessage.isNotificationVisible"
            severity="success"
            :msgText="useNotificationMessage.notificationMsg"
        />

        <UserDataTable
            :isApplicationSelected="isApplicationSelected"
            :loading="LoadingState.isLoading.value"
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

    label {
        margin-bottom: 0.5rem;
    }
}
</style>
