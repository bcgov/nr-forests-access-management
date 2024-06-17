<script setup lang="ts">
import { onUnmounted, ref, shallowRef, type PropType, computed } from 'vue';
import { useRoute } from 'vue-router';
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import TabView, { type TabViewChangeEvent } from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import router from '@/router';
import ManagePermissionsTitle from '@/components/managePermissions/ManagePermissionsTitle.vue';
import UserDataTable from '@/components/managePermissions/table/UserDataTable.vue';
import ApplicationAdminTable from '@/components/managePermissions/table/ApplicationAdminTable.vue';
import LoginUserState from '@/store/FamLoginUserState';
import {
    getCurrentTabState,
    setCurrentTabState,
} from '@/store/CurrentTabState';
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
    deleteAndRefreshUserRoleAssignments,
    deleteAndRefreshApplicationAdmin,
    fetchUserRoleAssignments,
    fetchApplicationAdmins,
    fetchDelegatedAdmins,
    deleteAndRefreshDelegatedAdmin,
} from '@/services/fetchData';
import { Severity } from '@/enum/SeverityEnum';
import { IconSize } from '@/enum/IconEnum';
import { TabKey } from '@/enum/TabEnum';

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

// get user access ids from router query parameters
const { query } = useRoute();

const newAppAdminId = ref((query.newAppAdminId as string) || '');
const newUserAccessIds = ref((query.newUserAccessIds as string) || '');
const newDelegatedAdminIds = ref((query.newDelegatedAdminIds as string) || '');

const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>(
    props.userRoleAssignments
);

const applicationAdmins = shallowRef<FamAppAdminGetResponse[]>(
    props.applicationAdmins
);

const delegatedAdmins = shallowRef<FamAccessControlPrivilegeGetResponse[]>(
    props.delegatedAdmins
);

const applicationsUserAdministers = computed(() => {
    return LoginUserState.getApplicationsUserAdministers();
});

const tabViewRef = ref();

const resetNewTag = () => {
    router.push({ query: {} });
    newAppAdminId.value = '';
    newUserAccessIds.value = '';
    newDelegatedAdminIds.value = '';
};

const resetNotificationAndNewRowTag = () => {
    resetNotification();
    resetNewTag();
};

onUnmounted(() => {
    resetNotificationAndNewRowTag();
});

const onApplicationSelected = async (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
    resetNotificationAndNewRowTag();

    if (e.value.id === FAM_APPLICATION_ID) {
        setCurrentTabState(TabKey.AdminAccess);
        applicationAdmins.value = await fetchApplicationAdmins();
    } else {
        if (!LoginUserState.isAdminOfSelectedApplication()) {
            setCurrentTabState(TabKey.UserAccess);
        }
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
    resetNotificationAndNewRowTag();

    try {
        userRoleAssignments.value = await deleteAndRefreshUserRoleAssignments(
            assignment.user_role_xref_id,
            assignment.role.application_id
        );

        setNotificationMsg(
            Severity.Success,
            `You removed ${assignment.role.role_name} access from ${assignment.user.user_name}`
        );
    } catch (error: any) {
        setNotificationMsg(
            Severity.Error,
            `An error has occured. ${error.response.data.detail.description}`
        );
    }
};

const deleteAppAdmin = async (admin: FamAppAdminGetResponse) => {
    resetNotificationAndNewRowTag();
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

const deleteDelegatedAdminAssignment = async (
    delegatedAdminAssignment: FamAccessControlPrivilegeGetResponse
) => {
    resetNotificationAndNewRowTag();
    try {
        delegatedAdmins.value = await deleteAndRefreshDelegatedAdmin(
            delegatedAdminAssignment.access_control_privilege_id
        );

        setNotificationMsg(
            Severity.Success,
            `You removed ${delegatedAdminAssignment.role.role_name} privilege from ${delegatedAdminAssignment.user.user_name}`
        );
    } catch (error: any) {
        setNotificationMsg(
            Severity.Error,
            `An error has occured. ${error.response.data.detail.description}`
        );
    }
};

// Tabs methods
const setCurrentTab = (event: TabViewChangeEvent) => {
    resetNotificationAndNewRowTag();
    setCurrentTabState(tabViewRef.value?.tabs[event.index].key);
};

const getCurrentTab = () => {
    const tabIndex = tabViewRef.value?.tabs
        .map((item: any) => {
            return item.key;
        })
        .indexOf(getCurrentTabState());
    return tabIndex > 0 ? tabIndex : 0;
};
</script>

<template>
    <ManagePermissionsTitle :isApplicationSelected="isApplicationSelected" />
    <div class="page-body">
        <div class="application-group">
            <label for="application-dropdown-id">
                You are modifying access in this application:
            </label>
            <Dropdown
                id="application-dropdown-id"
                name="application-dropdown-id"
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
                ref="tabViewRef"
                :active-index="getCurrentTab()"
                @tab-change="setCurrentTab($event)"
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
                    :key="TabKey.AdminAccess"
                    header="Application admins"
                    v-if="selectedApplicationId === FAM_APPLICATION_ID"
                >
                    <template #header>
                        <Icon icon="enterprise" :size="IconSize.small" />
                    </template>
                    <ApplicationAdminTable
                        :loading="isLoading()"
                        :applicationAdmins="applicationAdmins || []"
                        :newIds="newAppAdminId"
                        @deleteAppAdmin="deleteAppAdmin"
                    />
                </TabPanel>
                <TabPanel :key="TabKey.UserAccess" header="Users" v-else>
                    <template #header>
                        <Icon icon="user" :size="IconSize.small" />
                    </template>

                    <UserDataTable
                        :loading="isLoading()"
                        :userRoleAssignments="userRoleAssignments || []"
                        :newIds="newUserAccessIds"
                        @deleteUserRoleAssignment="deleteUserRoleAssignment"
                    />
                </TabPanel>

                <TabPanel
                    :key="TabKey.DelegatedAdminAccess"
                    v-if="
                        LoginUserState.isAdminOfSelectedApplication() &&
                        selectedApplicationId !== FAM_APPLICATION_ID
                    "
                    header="Delegated admins"
                >
                    <template #header>
                        <Icon icon="enterprise" :size="IconSize.small" />
                    </template>

                    <DelegatedAdminTable
                        :loading="isLoading()"
                        :delegatedAdmins="delegatedAdmins || []"
                        :newIds="newDelegatedAdminIds"
                        @deleteDelegatedAdminAssignment="
                            deleteDelegatedAdminAssignment
                        "
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
