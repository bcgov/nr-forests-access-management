<script setup lang="ts">
import ManagePermissionsTitle from "@/components/managePermissions/ManagePermissionsTitle.vue";
import ApplicationAdminTable from "@/components/managePermissions/table/ApplicationAdminTable.vue";
import DelegatedAdminTable from "@/components/managePermissions/table/DelegatedAdminTable.vue";
import TermsAndConditions from "@/components/common/TermsAndConditions.vue";
import UserDataTable from "@/components/managePermissions/table/UserDataTable.vue";
import { IconSize } from "@/enum/IconEnum";
import { Severity } from "@/enum/SeverityEnum";
import { TabKey } from "@/enum/TabEnum";
import { hashRouter } from "@/router";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import {
    deleteAndRefreshApplicationAdmin,
    deleteAndRefreshDelegatedAdmin,
    deleteAndRefreshUserRoleAssignments,
    fetchApplicationAdmins,
    fetchDelegatedAdmins,
    fetchUserRoleAssignments,
} from "@/services/fetchData";
import {
    isApplicationSelected,
    selectedApplication,
    selectedApplicationId,
    setSelectedApplication,
} from "@/store/ApplicationState";
import { FAM_APPLICATION_ID } from "@/store/Constants";
import {
    getCurrentTabState,
    setCurrentTabState,
} from "@/store/CurrentTabState";
import LoginUserState from "@/store/FamLoginUserState";
import { isLoading } from "@/store/LoadingState";
import {
    resetNotification,
    setNotificationMsg,
} from "@/store/NotificationState";
import type {
    FamAccessControlPrivilegeGetResponse,
    FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
import type { FamApplicationUserRoleAssignmentGetSchema } from "fam-app-acsctl-api";
import Dropdown, { type DropdownChangeEvent } from "primevue/dropdown";
import TabPanel from "primevue/tabpanel";
import TabView, { type TabViewChangeEvent } from "primevue/tabview";
import { computed, onUnmounted, ref, shallowRef, type PropType } from "vue";

const environmentSettings = new EnvironmentSettings();
const isDevEnvironment = environmentSettings.isDevEnvironment();

const props = defineProps({
    userRoleAssignments: {
        type: Array as PropType<FamApplicationUserRoleAssignmentGetSchema[]>,
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
    // router query parameters
    newAppAdminId: {
        type: String,
        default: "",
    },
    newUserAccessIds: {
        type: String,
        default: "",
    },
    newDelegatedAdminIds: {
        type: String,
        default: "",
    },
});

const userRoleAssignments = shallowRef<
    FamApplicationUserRoleAssignmentGetSchema[]
>(props.userRoleAssignments);

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
    hashRouter.push({ query: {} });
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
        if (isDevEnvironment)
            delegatedAdmins.value = await fetchDelegatedAdmins(
                selectedApplicationId.value
            );
    }
};

const deleteUserRoleAssignment = async (
    assignment: FamApplicationUserRoleAssignmentGetSchema
) => {
    resetNotificationAndNewRowTag();

    try {
        userRoleAssignments.value = await deleteAndRefreshUserRoleAssignments(
            assignment.user_role_xref_id,
            assignment.role.application.application_id
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
    <!-- TODO <TermsAndConditions /> -->
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
                        :newIds="props.newAppAdminId"
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
                        :newIds="props.newUserAccessIds"
                        @deleteUserRoleAssignment="deleteUserRoleAssignment"
                    />
                </TabPanel>

                <TabPanel
                    :key="TabKey.DelegatedAdminAccess"
                    v-if="
                        isDevEnvironment &&
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
                        :newIds="props.newDelegatedAdminIds"
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
@import "@/assets/styles/base.scss";

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
