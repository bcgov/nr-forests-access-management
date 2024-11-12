<script setup lang="ts">
import { ref } from "vue";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import { FilterMatchMode } from "primevue/api";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import {
    DEFAULT_ROW_PER_PAGE,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from "@/store/Constants";
import { getPermissionTableData } from "./utils";

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
    clientId: {
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
</script>

<template>
    <div class="my-permissions-table-container">
        <TableToolbar
            input-placeholder="search by application, environment, client numbers, company name, role, status, and more"
            @change="myPermissionsSearchChange"
            :filter="myPermissiosFilters['global'].value"
        />
        <DataTable
            v-model:filters="myPermissiosFilters"
            :value="adminUserAccessQuery.data.value"
            paginator
            :rows="DEFAULT_ROW_PER_PAGE"
            :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
            filterDisplay="menu"
            :globalFilterFields="['application', 'env', 'role', 'clientId']"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
            stripedRows
            removableSort
        >
            <template #empty> You have no accesses in FAM. </template>
            <Column header="Application" field="application" sortable>
                <template #body="{ data }">
                    <span>
                        {{ data.application }}
                    </span>
                </template>
            </Column>
            <Column field="env" header="Environment" sortable></Column>
            <Column field="clientId" header="Client Number" sortable> </Column>
            <Column header="Role" field="role" sortable>
                <template #body="{ data }">
                    {{ data.role }}
                </template>
            </Column>
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
