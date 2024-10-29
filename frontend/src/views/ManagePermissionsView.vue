<script setup lang="ts">
import { computed, ref, watch, type Component } from "vue";
import { isAxiosError } from "axios";
import { useQuery } from "@tanstack/vue-query";
import type { DropdownChangeEvent } from "primevue/dropdown";
import TabView, { type TabViewChangeEvent } from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import EnterpriseIcon from "@carbon/icons-vue/es/enterprise/16";
import UserIcon from "@carbon/icons-vue/es/user/16";

import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";

import PageTitle from "@/components/common/PageTitle.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import Dropdown from "@/components/UI/Dropdown.vue";
import TablePlaceholder from "@/components/managePermissions/TablePlaceholder.vue";
import { selectedApp, setSelectedApp } from "@/store/ApplicationState";
import {
    formatAxiosError,
    getUniqueApplications,
    isSelectedAppAuthorized,
} from "@/utils/ApiUtils";
import ManagePermissionsTable from "@/components/managePermissions/ManagePermissionsTable.vue";
import type {
    ManagePermissionsTabHeaderType,
    ManagePermissionsTabTypes,
} from "@/types/ManagePermissionsTypes";

const handleApplicatoinChange = (e: DropdownChangeEvent) => {
    setSelectedApp(e.value);
};

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
});

// Available tab keys and their visibility conditions
const tabs: ManagePermissionsTabTypes[] = [
    {
        key: AdminRoleAuthGroup.FamAdmin,
        visible: computed(() => selectedApp.value?.id === 1),
        icon: UserIcon as Component,
    },
    {
        key: AdminRoleAuthGroup.AppAdmin,
        visible: computed(() =>
            isSelectedAppAuthorized(
                "APP_ADMIN",
                selectedApp.value?.id,
                adminUserAccessQuery.data.value
            )
        ),
        icon: UserIcon as Component,
    },
    {
        key: AdminRoleAuthGroup.DelegatedAdmin,
        visible: computed(() =>
            isSelectedAppAuthorized(
                "DELEGATED_ADMIN",
                selectedApp.value?.id,
                adminUserAccessQuery.data.value
            )
        ),
        icon: EnterpriseIcon as Component,
    },
];

// Computed property to filter visible tabs dynamically
const visibleTabs = computed(() => tabs.filter((tab) => tab.visible.value));

const activeIndex = ref(0);

// Function to set `activeIndex` to the first visible tab
const updateActiveIndex = () => {
    activeIndex.value = 0;
};

// Watch `selectedApp` and call `updateActiveIndex`
watch(selectedApp, updateActiveIndex, { immediate: true });

const onTabChange = (event: TabViewChangeEvent) => {
    activeIndex.value = event.index;
};

const tabHeaders: ManagePermissionsTabHeaderType = {
    FAM_ADMIN: "Application admins",
    APP_ADMIN: "Users",
    DELEGATED_ADMIN: "Delegated admins",
};
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
            :is-fetching="adminUserAccessQuery.isFetching.value"
            :is-error="adminUserAccessQuery.isError.value"
            :error-msg="
                isAxiosError(adminUserAccessQuery.error.value)
                    ? formatAxiosError(adminUserAccessQuery.error.value)
                    : 'Failed to fetch data.'
            "
        />

        <div class="content-container">
            <TablePlaceholder v-if="!selectedApp" />
            <div v-else class="tab-view-container">
                <TabView :active-index="activeIndex" @tab-change="onTabChange">
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
                            :auth-group="tab.key"
                            :app-name="
                                selectedApp.description ?? selectedApp.name
                            "
                            :app-id="selectedApp.id"
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
