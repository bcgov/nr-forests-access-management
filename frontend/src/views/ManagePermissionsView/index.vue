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
    activeIndex,
} from "@/store/ApplicationState";
import {
    formatAxiosError,
    getUniqueApplications,
    isSelectedAppAuthorized,
} from "@/utils/ApiUtils";
import ManagePermissionsTable from "@/components/ManagePermissionsTable";
import type {
    PermissionNotificationType,
    ManagePermissionsTabHeaderType,
    ManagePermissionsTabTypes,
} from "@/types/ManagePermissionsTypes";
import NotificationStack from "@/views/ManagePermissionsView/NotificationStack.vue";
import {
    AppAdminErrorQuerykey,
    AppAdminSuccessQuerykey,
    DelegatedAdminErrorQueryKey,
    DelegatedAdminSuccessQueryKey,
    type AppPermissionQueryErrorType,
} from "../AddAppPermission/utils";
import type { FamUserRoleAssignmentRes } from "fam-app-acsctl-api/model";
import {
    generateAppErrorNotifications,
    generateAppSuccessNotifications,
    generateFamNotification,
} from "./utils";
import {
    FamPermissionErrorQueryKey,
    FamPermissionSuccessQueryKey,
} from "../AddFamPermission/utils";

const queryClient = useQueryClient();
const route = useRoute();
const router = useRouter();
const appIdFromQueryParam = ref(route.query.appId);

const environment = new EnvironmentSettings();

// Fetch notification Data
const appAdminSuccessData = queryClient.getQueryData<FamUserRoleAssignmentRes>([
    AppAdminSuccessQuerykey,
]);
const appAdminErrorData = queryClient.getQueryData<AppPermissionQueryErrorType>(
    [AppAdminErrorQuerykey]
);
const delegatedAdminSuccessData =
    queryClient.getQueryData<FamUserRoleAssignmentRes>([
        DelegatedAdminSuccessQueryKey,
    ]);
const delegatedAdminErrorData =
    queryClient.getQueryData<AppPermissionQueryErrorType>([
        DelegatedAdminErrorQueryKey,
    ]);
const FamPermissionSuccessData = queryClient.getQueryData<string>([
    FamPermissionSuccessQueryKey,
]);
const FamPermissionErrorData = queryClient.getQueryData<string>([
    FamPermissionErrorQueryKey,
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
                    "APP_ADMIN",
                    selectedApp.value?.id,
                    adminUserAccessQuery.data.value
                ) ||
                isSelectedAppAuthorized(
                    "DELEGATED_ADMIN",
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
                    "APP_ADMIN",
                    selectedApp.value?.id,
                    adminUserAccessQuery.data.value
                )
        ),
        icon: EnterpriseIcon as Component,
    },
];

const notifications = ref<PermissionNotificationType[]>([
    ...(appAdminSuccessData
        ? generateAppSuccessNotifications(
              "addUserPermission",
              appAdminSuccessData
          )
        : []),
    ...(delegatedAdminSuccessData
        ? generateAppSuccessNotifications(
              "addUserPermission",
              delegatedAdminSuccessData
          )
        : []),
    ...(appAdminErrorData
        ? [generateAppErrorNotifications(appAdminErrorData)]
        : []),
    ...(delegatedAdminErrorData
        ? [generateAppErrorNotifications(delegatedAdminErrorData)]
        : []),
    ...(FamPermissionSuccessData
        ? [generateFamNotification(true, FamPermissionSuccessData)]
        : []),
    ...(FamPermissionErrorData
        ? [generateFamNotification(false, FamPermissionErrorData)]
        : []),
]);

const clearNotifications = () => {
    queryClient.removeQueries({
        queryKey: [AppAdminSuccessQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AppAdminErrorQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [DelegatedAdminSuccessQueryKey],
    });
    queryClient.removeQueries({
        queryKey: [DelegatedAdminErrorQueryKey],
    });
    queryClient.removeQueries({
        queryKey: [FamPermissionSuccessQueryKey],
    });
    queryClient.removeQueries({
        queryKey: [FamPermissionErrorQueryKey],
    });
    notifications.value = [];
};

const addNotifications = (newNotifications: PermissionNotificationType[]) => {
    notifications.value.push(...newNotifications);
};

// Computed property to filter visible tabs dynamically
const visibleTabs = computed(() => tabs.filter((tab) => tab.visible.value));

// Function to set `activeIndex` to the first visible tab
const updateActiveIndex = () => {
    if (activeIndex.value >= visibleTabs.value.length) {
        activeIndex.value = 0;
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
    activeIndex.value = event.index;
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
                <TabView :active-index="activeIndex" @tab-change="onTabChange">
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
