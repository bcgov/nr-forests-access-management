<script setup lang="ts">
import ManagePermissionsTable from "@/components/ManagePermissionsTable";
import TablePlaceholder from "@/components/ManagePermissionsTable/TablePlaceholder.vue";
import Dropdown from "@/components/UI/Dropdown.vue";
import PageTitle from "@/components/UI/PageTitle.vue";
import Button from "@/components/UI/Button.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import {
    activeTabIndex,
    selectedApp,
    setSelectedApp,
} from "@/store/ApplicationState";
import {
    ManagePermissionsTableEnum,
    type ManagePermissionsTabHeaderType,
    type ManagePermissionsTabType,
} from "@/types/ManagePermissionsTypes";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import { formatAxiosError, getUniqueApplications } from "@/utils/ApiUtils";
import { isSelectedAppAuthorized } from "@/utils/AuthUtils";
import NotificationStack from "@/views/ManagePermissionsView/NotificationStack.vue";
import { AddAppPermissionRoute, AddFamPermissionRoute } from "@/router/routes";
import EnterpriseIcon from "@carbon/icons-vue/es/enterprise/16";
import UserIcon from "@carbon/icons-vue/es/user/16";
import AddIcon from "@carbon/icons-vue/es/add/16";
import { useQuery, useQueryClient } from "@tanstack/vue-query";
import { isAxiosError } from "axios";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import type { FamUserRoleAssignmentRes } from "fam-app-acsctl-api/model";
import type { DropdownChangeEvent } from "primevue/dropdown";
import TabPanel from "primevue/tabpanel";
import TabView, { type TabViewChangeEvent } from "primevue/tabview";
import { computed, onUnmounted, ref, watch, type Component } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
    AddAppUserPermissionErrorQuerykey,
    AddAppUserPermissionSuccessQuerykey,
    AddDelegatedAdminErrorQuerykey,
    AddDelegatedAdminSuccessQuerykey,
    type AppPermissionQueryErrorType,
} from "../AddAppPermission/utils";
import {
    AddFamPermissionErrorQueryKey,
    AddFamPermissionSuccessQueryKey,
} from "../AddFamPermission/utils";
import {
    generateAppPermissionErrorNotifications,
    generateAppPermissionSuccessNotifications,
    generateFamNotification,
} from "./utils";

const queryClient = useQueryClient();
const route = useRoute();
const router = useRouter();
const appIdFromQueryParam = ref(route.query.appId);

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

const handleApplicationChange = (e: DropdownChangeEvent) => {
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
const tabs: ManagePermissionsTabType[] = [
    {
        // Fam Application Admins Table
        key: ManagePermissionsTableEnum.AppAdmin,
        visible: computed(() => selectedApp.value?.id === 1),
        icon: UserIcon as Component,
    },
    {
        // App Specific User Table
        key: ManagePermissionsTableEnum.AppUser,
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
        // Delegated Admin table
        key: ManagePermissionsTableEnum.DelegatedAdmin,
        visible: computed(() =>
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
              addAppUserPermissionSuccessData,
              false
          )
        : []),
    ...(addDelegatedAdminSuccessData
        ? generateAppPermissionSuccessNotifications(
              addDelegatedAdminSuccessData,
              true
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

/**
 * Handle the add permission action
 */
const handleAddButton = () => {
    if (!selectedApp.value?.id) {
        return;
    }
    // FAM application id = 1
    else if (selectedApp.value.id === 1) {
        router.push({ name: AddFamPermissionRoute.name });
    } else {
        // App User table will have a tab index of 0
        // Delegated admin table will have a tab index of 1
        router.push({
            name: AddAppPermissionRoute.name,
            query: {
                appId: selectedApp.value?.id,
            },
        });
    }
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
    [ManagePermissionsTableEnum.AppAdmin]: "Application admins",
    [ManagePermissionsTableEnum.AppUser]: "Users",
    [ManagePermissionsTableEnum.DelegatedAdmin]: "Delegated admins",
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
        <div class="row dropdown-and-button-container">
            <!-- Dropdown -->
            <div class="col-lg-5 col-md-8 col-12 mb-3 mb-md-0">
                <Dropdown
                    id="application-selector-dropdown-id"
                    class="application-dropdown"
                    name="application-selector-dropdown"
                    label-text="Application:"
                    :value="selectedApp"
                    @change="handleApplicationChange"
                    :options="
                        getUniqueApplications(adminUserAccessQuery.data.value)
                    "
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
            </div>

            <!-- Button -->
            <div
                class="col-lg-3 col-md-3 col-12 d-flex justify-content-md-start justify-content-center"
            >
                <Button
                    v-if="selectedApp"
                    outlined
                    label="Add permission"
                    :icon="AddIcon"
                    @click="handleAddButton"
                />
            </div>
        </div>

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
                        :header="tabHeaders[tab.key]"
                    >
                        <template #header>
                            <component :is="tab.icon" />
                        </template>
                        <ManagePermissionsTable
                            :key="selectedApp.id"
                            class="tab-table"
                            :table-type="tab.key"
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
        width: 100%;
    }

    .dropdown-and-button-container {
        width: 100%;
        margin-top: 2.5rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: end;

        .fam-button {
            width: 100%;
            height: 3rem;
        }
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
