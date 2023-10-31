<script setup lang="ts">
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import { computed, onMounted, onUnmounted, shallowRef } from 'vue';

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

import { pushNotification, resetNotification } from '@/store/NotificationState';

import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';
import { Severity } from '@/enum/SeverityEnum';

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
    resetNotification();
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
    pushNotification(
        Severity.success,
        `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`
    );
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
                placeholder="Choose an application to manage permissions"
                class="application-dropdown"
            />
        </div>

        <div class="dashboard-background-layout">
            <NotificationStack />
            <UserDataTable
                :isApplicationSelected="isApplicationSelected"
                :loading="LoadingState.isLoading.value"
                :userRoleAssignments="userRoleAssignments || []"
                :selectedApplicationDisplayText="selectedApplicationDisplayText"
                @deleteUserRoleAssignment="deleteUserRoleAssignment"
            />
        </div>
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';

.application-group {
    display: grid;

    label {
        margin-bottom: 0.5rem;
    }
}
.application-dropdown {
    max-width: calc(100vw - 3rem);
    height: 3rem;
    padding: 0;

    &:deep(.p-dropdown-label) {
        padding: 0.8375rem 1rem;
    }
}

.dashboard-background-layout {
    overflow-y: scroll;
    margin-top: 3rem;
    padding: 1rem 0rem;
    background: $light-layer-one;
    z-index: -1;
    min-height: calc(100vh - 17.4rem);
}

@media (min-width: 495px) {
    .application-dropdown {
        max-width: 29rem;
    }
}

@media (min-width: 768px) {
    .dashboard-background-layout {
        width: calc(100vw - 16rem) !important;
        margin-left: -2.5rem;
        min-height: calc(100vh - 17.1rem);
    }
}

@media (min-width: 1024px) {
    .application-dropdown {
        max-width: 38rem;
    }
}
</style>
