<script setup lang="ts">
import { ref } from "vue";
import { isAxiosError } from "axios";
import { useQuery } from "@tanstack/vue-query";
import type { DropdownChangeEvent } from "primevue/dropdown";
import type { FamApplicationDto } from "fam-admin-mgmt-api/model";

import PageTitle from "@/components/common/PageTitle.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import Dropdown from "@/components/UI/Dropdown.vue";
import { formatAxiosError, getUniqueApplications } from "@/utils/ApiUtils";
import TablePlaceholder from "@/components/managePermissions/table/TablePlaceholder.vue";

const selectedApp = ref<FamApplicationDto>();

const handleApplicatoinChange = (e: DropdownChangeEvent) => {
    selectedApp.value = e.value;
    console.log(selectedApp.value);
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

        <div class="tab-container">
            <TablePlaceholder v-if="!selectedApp" />
        </div>
    </div>
</template>

<style lang="scss">
.manage-permission-view {
    .application-dropdown {
        margin-top: 2.5rem;
    }

    .tab-container {
        margin: 2.5rem -2.5rem 0 -2.5rem;
        background: var(--layer-01);
    }
}
</style>
