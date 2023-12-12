<script setup lang="ts">
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import { onUnmounted, shallowRef, type PropType } from 'vue';

import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/UserDataTable.vue';
import { Severity } from '@/enum/SeverityEnum';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    selectedApplicationDisplayText,
    setSelectedApplication,
} from '@/store/ApplicationState';
import LoadingState from '@/store/LoadingState';
import {
    resetNotification,
    setNotificationMsg,
} from '@/store/NotificationState';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import {
    deletAndRefreshUserRoleAssignments,
    fetchUserRoleAssignments,
} from '@/services/fetchData';

const props = defineProps({
    userRoleAssignments: {
        type: Array as PropType<FamApplicationUserRoleAssignmentGet[]>,
        default: [],
    },
});

const userRoleAssignments = shallowRef<
    FamApplicationUserRoleAssignmentGet[]
>(props.userRoleAssignments);

onUnmounted(() => {
    resetNotification();
});

const onApplicationSelected = async (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
    userRoleAssignments.value = await fetchUserRoleAssignments(selectedApplication.value?.application_id);
};

async function deleteUserRoleAssignment(
    assignment: FamApplicationUserRoleAssignmentGet
) {
    try {
        userRoleAssignments.value = await deletAndRefreshUserRoleAssignments(
            assignment.user_role_xref_id,
            assignment.role.application_id
        );

        setNotificationMsg(
            Severity.success,
            `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`
        );
    } catch (error: any) {
        setNotificationMsg(
            Severity.error,
            `An error has occured. ${error.response.data.detail.description}`
        );
    }
}
</script>

<template>
    <ManagePermissionsTitle :isApplicationSelected="isApplicationSelected" />

    <div class="page-body">
        <div class="application-group">
            <label>You are modifying access in this application:</label>
            <Dropdown
                v-model="selectedApplication"
                @change="onApplicationSelected"
                :options="applicationsUserAdministers"
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
    margin-top: 3rem;
    padding: 1rem 0rem;
    background: $light-layer-one;
    z-index: -1;
    margin-left: -2.5rem !important;
    min-height: calc(100vh - 19.125rem) !important;
    width: calc(100vw + 3rem) !important;
}

@media (min-width: 495px) {
    .application-dropdown {
        max-width: 29rem;
    }
}

@media (min-width: 768px) {
    .dashboard-background-layout {
        width: 100vw !important;
    }
}

@media (min-width: 1024px) {
    .application-dropdown {
        max-width: 38rem;
    }

    .dashboard-background-layout {
        width: calc(100vw - 16rem) !important;
    }
}
</style>
