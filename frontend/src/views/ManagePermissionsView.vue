<script setup lang="ts">
import PageTitle from "@/components/common/PageTitle.vue";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { useQuery } from "@tanstack/vue-query";
import type { DropdownChangeEvent } from "primevue/dropdown";
import Dropdown from "@/components/UI/Dropdown.vue";
import type { FamApplicationDto } from "fam-admin-mgmt-api/model";
import { ref } from "vue";

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
    select: (data): FamApplicationDto[] => {
        return Array.from(
            data.access
                .flatMap((authGrant) =>
                    authGrant.grants.map((grant) => grant.application)
                )
                .reduce((acc, app) => acc.set(app.id, app), new Map())
                .values()
        );
    },
});
</script>

<template>
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
        :options="adminUserAccessQuery.data.value"
        option-label="description"
        placeholder="Choose an application to manage permissions"
        :is-fetching="adminUserAccessQuery.isFetching.value"
    />
</template>

<style lang="scss" scoped>
.application-dropdown {
    margin-top: 2.5rem;
}
</style>
