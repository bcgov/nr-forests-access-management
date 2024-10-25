<script setup lang="ts">
import { isAxiosError } from "axios";
import { useQuery } from "@tanstack/vue-query";
import type { DropdownChangeEvent } from "primevue/dropdown";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";

import PageTitle from "@/components/common/PageTitle.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import Dropdown from "@/components/UI/Dropdown.vue";
import {
    formatAxiosError,
    getUniqueApplications,
    isSelectedAppAuthorized,
} from "@/utils/ApiUtils";
import TablePlaceholder from "@/components/managePermissions/table/TablePlaceholder.vue";
import { selectedApp, setSelectedApp } from "@/store/ApplicationState";

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
                <TabView>
                    <TabPanel
                        header="Application admins"
                        v-if="selectedApp.id === 1"
                    >
                    </TabPanel>
                    <TabPanel
                        header="Users"
                        v-if="
                            isSelectedAppAuthorized(
                                selectedApp.id,
                                'APP_ADMIN',
                                adminUserAccessQuery.data.value
                            )
                        "
                    >
                    </TabPanel>
                    <TabPanel
                        header="Delegated admins"
                        v-if="
                            isSelectedAppAuthorized(
                                selectedApp.id,
                                'DELEGATED_ADMIN',
                                adminUserAccessQuery.data.value
                            )
                        "
                    >
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
}
</style>
