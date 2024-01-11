<script setup lang="ts">
import { onUnmounted, shallowRef, computed, type PropType } from 'vue';
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/table/UserDataTable.vue';
import ApplicationAdminTable from './table/ApplicationAdminTable.vue';

import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    setSelectedApplication,
    selectedApplicationShortDisplayText
} from '@/store/ApplicationState';
import { isLoading } from '@/store/LoadingState';
import {
    resetNotification,
    setNotificationMsg,
} from '@/store/NotificationState';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import type { FamAppAdminGet } from 'fam-admin-mgmt-api/model';
import {
    deletAndRefreshUserRoleAssignments,
    deleteAndRefreshApplicationAdmin,
    fetchUserRoleAssignments,
    fetchApplicationAdmin
} from '@/services/fetchData';
import { Severity } from '@/enum/SeverityEnum';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps({
    userRoleAssignments: {
        type: Array as PropType<FamApplicationUserRoleAssignmentGet[]>,
        default: [],
    },
    applicationAdmins: {
        type: Array as PropType<FamAppAdminGet[]>,
        default: [],
    },
});

const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>(
    props.userRoleAssignments
);

const applicationAdmins = shallowRef<
    FamAppAdminGet[]
>(props.applicationAdmins);

onUnmounted(() => {
    resetNotification();
});

const tabHeader = computed(() => {
    return selectedApplicationShortDisplayText.value === 'FAM'
            ? 'Application admins'
            : 'Users';
})

const onApplicationSelected = async (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
    if(e.value.application_id === 2) {
        userRoleAssignments.value = await fetchUserRoleAssignments(
            selectedApplication.value?.application_id
        );
    } else if (e.value.application_id === 1) {
        applicationAdmins.value = await fetchApplicationAdmin(
            selectedApplication.value?.application_id
        );
    }
};

const deleteUserRoleAssignment = async (
    assignment: FamApplicationUserRoleAssignmentGet
) => {
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

const deleteAppAdmin = async ( admin: FamAppAdminGet) => {
    try {
        applicationAdmins.value = await deleteAndRefreshApplicationAdmin(
            admin.application_admin_id,
            admin.application_id
        );

        setNotificationMsg(
            Severity.success,
            `You removed ${admin.user.user_name}'s admin privilege`
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
            <TablePlaceholder v-if="!isApplicationSelected" />
            <TabView
                v-else
                :pt="{
                    root: {
                        style: 'margin-top: 1.5rem',
                    },
                    panelContainer: {
                        style: 'margin-top: -0.0625rem;',
                    },
                }"
            >
                <TabPanel :header="tabHeader">
                    <template #header>
                        <Icon icon="user" :size="IconSize.small" />
                    </template>
                    <UserDataTable
                        v-if="selectedApplicationShortDisplayText == 'FOM_DEV'"
                        :loading="isLoading()"
                        :userRoleAssignments="userRoleAssignments || []"
                        @deleteUserRoleAssignment="deleteUserRoleAssignment"
                    />
                    <ApplicationAdminTable
                        v-if="selectedApplicationShortDisplayText == 'FAM'"
                        :loading="isLoading()"
                        :applicationAdmins="applicationAdmins || []"
                        @deleteAppAdmin="deleteAppAdmin"
                    />
                </TabPanel>
                <!-- waiting for the Delegated admins table
                <TabPanel
                    header="Delegated admins"
                    :disabled="false"
                >
                    <template #header>
                        <Icon
                            icon="enterprise"
                            :size="IconSize.small"
                        />
                    </template>
                </TabPanel>  -->
            </TabView>
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
    margin-left: -2.5rem !important;
    padding: 1rem 2.5rem;
    background: $light-layer-one;
    z-index: -1;
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
