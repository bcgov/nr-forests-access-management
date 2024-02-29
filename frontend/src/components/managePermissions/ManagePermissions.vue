<script setup lang="ts">
import { onUnmounted, ref, shallowRef, type PropType, computed } from 'vue';
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/table/UserDataTable.vue';
import ApplicationAdminTable from '@/components/managePermissions/table/ApplicationAdminTable.vue';
import LoginUserState from '@/store/FamLoginUserState';
import DelegatedAdminTable from '@/components/managePermissions/table/DelegatedAdminTable.vue';
import {
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
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import type {
    FamAccessControlPrivilegeGetResponse,
    FamAppAdminGetResponse,
} from 'fam-admin-mgmt-api/model';
import {
    deletAndRefreshUserRoleAssignments,
    deleteAndRefreshApplicationAdmin,
    fetchUserRoleAssignments,
    fetchApplicationAdmins,
    fetchDelegatedAdmins,
} from '@/services/fetchData';
import { Severity } from '@/enum/SeverityEnum';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps({
    userRoleAssignments: {
        type: Array as PropType<FamApplicationUserRoleAssignmentGet[]>,
        default: [],
    },
    applicationAdmins: {
        type: Array as PropType<FamAppAdminGetResponse[]>,
        default: [],
    },
    delegatedAdmins: {
        type: Array as PropType<FamAccessControlPrivilegeGetResponse[]>,
        default: [],
    },
});

const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>(
    props.userRoleAssignments
);

const applicationAdmins = shallowRef<FamAppAdminGetResponse[]>(
    props.applicationAdmins
);

const delegatedAdmins = shallowRef<FamAccessControlPrivilegeGetResponse[]>(
    props.delegatedAdmins
);

const resetActiveTab = ref(0);

const applicationsUserAdministers = computed(() => {
    return LoginUserState.getApplicationsUserAdministers();
});

onUnmounted(() => {
    resetNotification();
});

const onApplicationSelected = async (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);

    // make the first tab active
    resetActiveTab.value = 0;
    if (e.value.id === FAM_APPLICATION_ID) {
        applicationAdmins.value = await fetchApplicationAdmins();
    } else {
        userRoleAssignments.value = await fetchUserRoleAssignments(
            selectedApplicationId.value
        );

        delegatedAdmins.value = await fetchDelegatedAdmins(
            selectedApplicationId.value
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
            Severity.Success,
            `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`
        );
    } catch (error: any) {
        setNotificationMsg(
            Severity.Error,
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
            Severity.Success,
            `You removed ${admin.user.user_name}'s admin privilege`
        );
    } catch (error: any) {
        setNotificationMsg(
            Severity.Error,
            `An error has occured. ${error.response.data.detail.description}`
        );
    }
};
</script>

<template>
    <ManagePermissionsTitle :isApplicationSelected="isApplicationSelected" />
    {{ LoginUserState.state.value.famLoginUser?.accesses }}
    <div class="page-body">
        <div class="application-group">
            <label>You are modifying access in this application:</label>
            <Dropdown
                v-model="selectedApplication"
                @change="onApplicationSelected"
                :options="applicationsUserAdministers"
                optionLabel="description"
                placeholder="Choose an application to manage permissions"
                class="application-dropdown"
            />
        </div>

        <div class="dashboard-background-layout">
            <NotificationStack />
            <TablePlaceholder v-if="!isApplicationSelected" />
            <TabView
                v-else
                v-model:active-index="resetActiveTab"
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
                        <Icon
                            icon="enterprise"
                            :size="IconSize.small"
                        />
                    </template>
                    <ApplicationAdminTable
                        :loading="isLoading()"
                        :applicationAdmins="applicationAdmins || []"
                        @deleteAppAdmin="deleteAppAdmin"
                    />
                </TabPanel>
                <TabPanel
                    header="Users"
                    v-else
                >
                    <template #header>
                        <Icon
                            icon="user"
                            :size="IconSize.small"
                        />
                    </template>

                    <UserDataTable
                        :loading="isLoading()"
                        :userRoleAssignments="userRoleAssignments || []"
                        @deleteUserRoleAssignment="deleteUserRoleAssignment"
                    />
                </TabPanel>

                <TabPanel
                    v-if="
                        LoginUserState.isAdminOfSelectedApplication() &&
                        selectedApplicationId !== FAM_APPLICATION_ID
                    "
                    header="Delegated admins"
                >
                    <template #header>
                        <Icon
                            icon="enterprise"
                            :size="IconSize.small"
                        />
                    </template>

                    <DelegatedAdminTable
                        :loading="isLoading()"
                        :delegatedAdmins="delegatedAdmins || []"
                    />
                </TabPanel>
            </TabView>
        </div>
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
.application-group {
    display: grid;
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
