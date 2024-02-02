<script setup lang="ts">
import { onUnmounted, shallowRef, type PropType, watch } from 'vue';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/table/UserDataTable.vue';
import ApplicationAdminTable from '@/components/managePermissions/table/ApplicationAdminTable.vue';
import ApplicationSelect from '@/components/common/ApplicationSelect.vue';

import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    setSelectedApplication,
    selectedApplicationId,
} from '@/store/ApplicationState';
import { isLoading } from '@/store/LoadingState';
import {
    resetNotification,
    setNotificationMsg,
} from '@/store/NotificationState';

import { FAM_APPLICATION_ID } from '@/store/Constants';
import { Severity } from '@/enum/SeverityEnum';
import { IconSize } from '@/enum/IconEnum';
import type {
    FamApplication,
    FamApplicationUserRoleAssignmentGet,
} from 'fam-app-acsctl-api';
import type { FamAppAdminGetResponse } from 'fam-admin-mgmt-api/model';
import {
    deletAndRefreshUserRoleAssignments,
    deleteAndRefreshApplicationAdmin,
    fetchUserRoleAssignments,
    fetchApplicationAdmins,
} from '@/services/fetchData';

const props = defineProps({
    userRoleAssignments: {
        type: Array as PropType<FamApplicationUserRoleAssignmentGet[]>,
        default: [],
    },
    applicationAdmins: {
        type: Array as PropType<FamAppAdminGetResponse[]>,
        default: [],
    },
});

const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>(
    props.userRoleAssignments
);

const applicationAdmins = shallowRef<FamAppAdminGetResponse[]>(
    props.applicationAdmins
);

const manageApplicationSelected = shallowRef<FamApplication>(
    selectedApplication.value as FamApplication
);

onUnmounted(() => {
    resetNotification();
});

watch(manageApplicationSelected, async (newManageApplicationSelected) => {
    setSelectedApplication(
        newManageApplicationSelected
            ? JSON.stringify(newManageApplicationSelected)
            : null
    );
    if (newManageApplicationSelected?.application_id === FAM_APPLICATION_ID) {
        applicationAdmins.value = await fetchApplicationAdmins();
    } else {
        userRoleAssignments.value = await fetchUserRoleAssignments(
            selectedApplicationId.value
        );
    }
});

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
};

const deleteAppAdmin = async (admin: FamAppAdminGetResponse) => {
    try {
        applicationAdmins.value = await deleteAndRefreshApplicationAdmin(
            admin.application_admin_id
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
};
</script>

<template>
    <ManagePermissionsTitle :isApplicationSelected="isApplicationSelected" />

    <div class="page-body">
        <div class="application-group">
            <ApplicationSelect
                v-model="manageApplicationSelected"
                :options="applicationsUserAdministers"
                label="You are modifying access in this application:"
                placeholder="Choose an application to manage permissions"
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
                <TabPanel
                    header="Application admins"
                    v-if="selectedApplicationId === FAM_APPLICATION_ID"
                >
                    <template #header>
                        <Icon icon="enterprise" :size="IconSize.small" />
                    </template>
                    <ApplicationAdminTable
                        :loading="isLoading()"
                        :applicationAdmins="applicationAdmins || []"
                        @deleteAppAdmin="deleteAppAdmin"
                    />
                </TabPanel>
                <TabPanel header="Users" v-else>
                    <template #header>
                        <Icon icon="user" :size="IconSize.small" />
                    </template>

                    <UserDataTable
                        :loading="isLoading()"
                        :userRoleAssignments="userRoleAssignments || []"
                        @deleteUserRoleAssignment="deleteUserRoleAssignment"
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

.dashboard-background-layout {
    margin-top: 3rem;
    margin-left: -2.5rem !important;
    padding: 1rem 2.5rem;
    background: $light-layer-one;
    z-index: -1;
    min-height: calc(100vh - 19.125rem) !important;
    width: calc(100vw + 3rem) !important;
}

@media (min-width: 768px) {
    .dashboard-background-layout {
        width: 100vw !important;
    }
}

@media (min-width: 1024px) {
    .dashboard-background-layout {
        width: calc(100vw - 16rem) !important;
    }
}
</style>
