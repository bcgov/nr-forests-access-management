<script setup lang="ts">
import { isAxiosError } from "axios";
import { ref } from "vue";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import { FilterMatchMode } from "primevue/api";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";

import TableSkeleton from "../Skeletons/TableSkeleton.vue";
import { formatAxiosError } from "@/utils/ApiUtils";
import ErrorText from "../UI/ErrorText.vue";
import {
    DEFAULT_ROW_PER_PAGE,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from "@/constants/constants";
import { getPermissionTableData } from "./utils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";

const myPermissiosFilters = ref({
    global: { value: "", matchMode: FilterMatchMode.CONTAINS },
    application: {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    env: {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    forestClient: {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    role: {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
});

const myPermissionsSearchChange = (newvalue: string) => {
    myPermissiosFilters.value.global.value = newvalue;
};

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => getPermissionTableData(data.access),
    refetchOnMount: true,
});

const headers: string[] = [
    "Application",
    "Environment",
    "Organization",
    "Role",
];
</script>

<template>
    <div class="my-permissions-table-container">
        <TableToolbar
            input-placeholder="search by application, environment, organization, role, status, and more"
            @change="myPermissionsSearchChange"
            :filter="myPermissiosFilters['global'].value"
        />
        <TableSkeleton
            v-if="adminUserAccessQuery.isLoading.value"
            :headers="headers"
            :row-amount="5"
        />
        <ErrorText
            v-else-if="adminUserAccessQuery.isError.value"
            :error-msg="
                isAxiosError(adminUserAccessQuery.error.value)
                    ? `Failed to fetch data. ${formatAxiosError(
                          adminUserAccessQuery.error.value
                      )}`
                    : 'Failed to fetch data.'
            "
        />
        <DataTable
            v-else
            v-model:filters="myPermissiosFilters"
            :value="adminUserAccessQuery.data.value"
            paginator
            :rows="DEFAULT_ROW_PER_PAGE"
            :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
            filterDisplay="menu"
            :globalFilterFields="['application', 'env', 'role', 'forestClient']"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
            stripedRows
            removableSort
        >
            <template #empty> You have no accesses in FAM. </template>

            <Column :header="headers[0]" field="application" sortable> </Column>

            <Column field="env" :header="headers[1]" sortable></Column>

            <Column field="forestClient" :header="headers[2]" sortable>
                <template #body="{ data }">
                    {{
                        formatForestClientDisplayName(
                            data.forestClient?.split(" ")[0],
                            data.forestClient?.split(" ").slice(1).join(" ")
                        )
                    }}
                </template>
            </Column>

            <Column field="role" :header="headers[3]" sortable />
        </DataTable>
    </div>
</template>

<style lang="scss">
.my-permissions-table-container {
    .p-datatable {
        .p-column-title {
            padding: 1rem 0;
        }

        .p-paginator {
            // Not sure why the border is gone with this,
            // probably some stupid $hit in frontend/node_modules/@bcgov-nr/nr-theme/style-sheets/primevue-components-overrides.scss
            border: 1px solid #dee2e6;
            border-radius: 0;
        }

        .p-sortable-column-icon {
            margin-bottom: 0;
        }
    }
}
</style>
