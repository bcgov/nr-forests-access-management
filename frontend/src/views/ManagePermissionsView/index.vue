<script setup lang="ts">
import { computed, onUnmounted, ref, watch, type Component } from "vue";
import { useRoute, useRouter } from "vue-router";
import { isAxiosError } from "axios";
import { useQuery, useQueryClient } from "@tanstack/vue-query";
import type { DropdownChangeEvent } from "primevue/dropdown";
import TabView, { type TabViewChangeEvent } from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import EnterpriseIcon from "@carbon/icons-vue/es/enterprise/16";
import UserIcon from "@carbon/icons-vue/es/user/16";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import PageTitle from "@/components/UI/PageTitle.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import Dropdown from "@/components/UI/Dropdown.vue";
import TablePlaceholder from "@/components/ManagePermissionsTable/TablePlaceholder.vue";
import {
    selectedApp,
    setSelectedApp,
    activeTabIndex,
} from "@/store/ApplicationState";
import {
    formatAxiosError,
    getUniqueApplications,
    isSelectedAppAuthorized,
} from "@/utils/ApiUtils";
import ManagePermissionsTable from "@/components/ManagePermissionsTable";
import type {
    ManagePermissionsTabHeaderType,
    ManagePermissionsTabTypes,
} from "@/types/ManagePermissionsTypes";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import NotificationStack from "@/views/ManagePermissionsView/NotificationStack.vue";
import {
    AddAppUserPermissionErrorQuerykey,
    AddAppUserPermissionSuccessQuerykey,
    AddDelegatedAdminErrorQuerykey,
    AddDelegatedAdminSuccessQuerykey,
    type AppPermissionQueryErrorType,
} from "../AddAppPermission/utils";
import type { FamUserRoleAssignmentRes } from "fam-app-acsctl-api/model";
import {
    generateAppPermissionErrorNotifications,
    generateAppPermissionSuccessNotifications,
    generateFamNotification,
} from "./utils";
import {
    AddFamPermissionErrorQueryKey,
    AddFamPermissionSuccessQueryKey,
} from "../AddFamPermission/utils";

const queryClient = useQueryClient();
const route = useRoute();
const router = useRouter();
const appIdFromQueryParam = ref(route.query.appId);

const environment = new EnvironmentSettings();

// Fetch notification Data
const addAppUserPermissionSuccessData =
    queryClient.getQueryData<FamUserRoleAssignmentRes>([
        AddAppUserPermissionSuccessQuerykey,
    ]);
const addAppUserPermissionErrorData =
    queryClient.getQueryData<AppPermissionQueryErrorType>([
        AddAppUserPermissionErrorQuerykey,
    ]);
const addDelegatedAdminSuccessData =
    queryClient.getQueryData<FamUserRoleAssignmentRes>([
        AddDelegatedAdminSuccessQuerykey,
    ]);
const addDelegatedAdminErrorData =
    queryClient.getQueryData<AppPermissionQueryErrorType>([
        AddDelegatedAdminErrorQuerykey,
    ]);
const addFamPermissionSuccessData = queryClient.getQueryData<string>([
    AddFamPermissionSuccessQueryKey,
]);
const addFamPermissionErrorData = queryClient.getQueryData<string>([
    AddFamPermissionErrorQueryKey,
]);

const handleApplicatoinChange = (e: DropdownChangeEvent) => {
    setSelectedApp(e.value);
    router.replace({ query: { appId: e.value.id } });
    clearNotifications();
};

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    refetchOnMount: true,
});

watch(
    [appIdFromQueryParam, selectedApp, adminUserAccessQuery.isFetched],
    ([appId, currentApp, isFetched]) => {
        // If `appIdFromQueryParam` exists and `selectedApp` is undefined, set the selected app
        if (appId && !currentApp && isFetched) {
            const foundApp = getUniqueApplications(
                adminUserAccessQuery.data.value
            ).find(
                (famApplicationDto) => famApplicationDto.id === Number(appId)
            );
            if (foundApp) {
                setSelectedApp(foundApp);
            }
        }
    },
    { immediate: true } // Run immediately to catch initial load
);

// Available tab keys and their visibility conditions
const tabs: ManagePermissionsTabTypes[] = [
    {
        key: AdminRoleAuthGroup.FamAdmin,
        visible: computed(() => selectedApp.value?.id === 1),
        icon: UserIcon as Component,
    },
    {
        key: AdminRoleAuthGroup.AppAdmin,
        visible: computed(
            () =>
                isSelectedAppAuthorized(
                    AdminRoleAuthGroup.AppAdmin,
                    selectedApp.value?.id,
                    adminUserAccessQuery.data.value
                ) ||
                isSelectedAppAuthorized(
                    AdminRoleAuthGroup.DelegatedAdmin,
                    selectedApp.value?.id,
                    adminUserAccessQuery.data.value
                )
        ),
        icon: UserIcon as Component,
    },
    {
        key: AdminRoleAuthGroup.DelegatedAdmin,
        visible: computed(
            () =>
                // DelegatedAdminFeatureFlag
                !environment.isProdEnvironment() &&
                isSelectedAppAuthorized(
                    AdminRoleAuthGroup.AppAdmin,
                    selectedApp.value?.id,
                    adminUserAccessQuery.data.value
                )
        ),
        icon: EnterpriseIcon as Component,
    },
];

// This computed property dynamically adjusts the displayed tabs to align with the available permissions
// and the app’s setup for different user roles and environments.
const visibleTabs = computed(() => tabs.filter((tab) => tab.visible.value));

const notifications = ref<PermissionNotificationType[]>([
    ...(addAppUserPermissionSuccessData
        ? generateAppPermissionSuccessNotifications(
              "addUserPermission",
              addAppUserPermissionSuccessData
          )
        : []),
    ...(addDelegatedAdminSuccessData
        ? generateAppPermissionSuccessNotifications(
              "addUserPermission",
              addDelegatedAdminSuccessData
          )
        : []),
    ...(addAppUserPermissionErrorData
        ? [
              generateAppPermissionErrorNotifications(
                  addAppUserPermissionErrorData
              ),
          ]
        : []),
    ...(addDelegatedAdminErrorData
        ? [generateAppPermissionErrorNotifications(addDelegatedAdminErrorData)]
        : []),
    ...(addFamPermissionSuccessData
        ? [generateFamNotification(true, addFamPermissionSuccessData)]
        : []),
    ...(addFamPermissionErrorData
        ? [generateFamNotification(false, addFamPermissionErrorData)]
        : []),
]);

const clearNotifications = () => {
    queryClient.removeQueries({
        queryKey: [AddAppUserPermissionSuccessQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddAppUserPermissionErrorQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddDelegatedAdminSuccessQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddDelegatedAdminErrorQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddFamPermissionSuccessQueryKey],
    });
    queryClient.removeQueries({
        queryKey: [AddFamPermissionErrorQueryKey],
    });
    notifications.value = [];
};

const addNotifications = (newNotifications: PermissionNotificationType[]) => {
    notifications.value = newNotifications;
};

// Function to set `activeTabIndex` to the first visible tab
const updateActiveIndex = () => {
    if (activeTabIndex.value >= visibleTabs.value.length) {
        activeTabIndex.value = 0;
    }
};

// Watch `selectedApp` and call `updateActiveIndex`
watch(
    selectedApp,
    () => {
        updateActiveIndex();
    },
    { immediate: true }
);

const onTabChange = (event: TabViewChangeEvent) => {
    activeTabIndex.value = event.index;
    clearNotifications();
};

const tabHeaders: ManagePermissionsTabHeaderType = {
    FAM_ADMIN: "Application admins",
    APP_ADMIN: "Users",
    DELEGATED_ADMIN: "Delegated admins",
};

const onNotificationClose = (idx: number) => {
    notifications.value.splice(idx, 1);
};

// Clear notifications data
onUnmounted(() => {
    clearNotifications();
});
</script>

<template>
    <div class="manage-permission-view">
        <PageTitle
            title="Manage permissions"
            subtitle="Manage users and add permissions for the selected application"
        />
        <Dropdown
            id="application-selector-dropdown-id"
            class="application-dropdown"
            name="application-selector-dropdown"
            label-text="Application:"
            :value="selectedApp"
            @change="handleApplicatoinChange"
            :options="getUniqueApplications(adminUserAccessQuery.data.value)"
            option-label="description"
            placeholder="Choose an application to manage permissions"
            :is-fetching="adminUserAccessQuery.isLoading.value"
            :is-error="adminUserAccessQuery.isError.value"
            :error-msg="
                isAxiosError(adminUserAccessQuery.error.value)
                    ? formatAxiosError(adminUserAccessQuery.error.value)
                    : 'Failed to fetch data.'
            "
        />

        <div class="content-container">
            <NotificationStack
                :permission-notifications="notifications"
                :on-close="onNotificationClose"
            />
            <TablePlaceholder v-if="!selectedApp" />
            <div v-else class="tab-view-container">
                <TabView
                    :active-index="activeTabIndex"
                    @tab-change="onTabChange"
                >
                    <TabPanel
                        v-for="tab in visibleTabs"
                        :key="tab.key"
                        :header="tabHeaders[tab.key as AdminRoleAuthGroup]"
                    >
                        <template #header>
                            <component :is="tab.icon" />
                        </template>
                        <ManagePermissionsTable
                            :key="selectedApp.id"
                            class="tab-table"
                            :auth-group="tab.key"
                            :app-name="
                                selectedApp.description ?? selectedApp.name
                            "
                            :app-id="selectedApp.id"
                            :add-notifications="addNotifications"
                        />
                    </TabPanel>
                </TabView>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.manage-permission-view {
    .application-dropdown {
        margin-top: 2.5rem;
    }

    .content-container {
        display: flex;
        flex-direction: column;
        margin: 2.5rem -2.5rem 0 -2.5rem;
        background: var(--layer-01);
        min-height: calc(100vh - 19rem);
        padding: 2.5rem;
    }

    .p-tabview-header {
        .p-tabview-nav-link {
            height: 3rem;
        }
    }
    .tab-table {
        margin-top: -0.0625rem;
    }
}
</style>
