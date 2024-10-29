<script setup lang="ts">
import { ref } from "vue";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import ProgressSpinner from "primevue/progressspinner";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import { FilterMatchMode } from "primevue/api";
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from "@/store/Constants";
import { isLoading } from "@/store/LoadingState";

import FamLoginUserState from "@/store/FamLoginUserState";

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
</script>

<template>
    <div class="my-permissions-table-wrapper">
        <TableToolbar
            input-placeholder="search by application, environment, client numbers, company name, role, status, and more"
            @change="myPermissionsSearchChange"
            :filter="myPermissiosFilters['global'].value"
        />
        <DataTable
            class="custom-data-table"
            v-model:filters="myPermissiosFilters"
            :value="FamLoginUserState.getMyAdminPermission()"
            paginator
            :rows="50"
            :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
            filterDisplay="menu"
            :loading="isLoading()"
            :globalFilterFields="['application', 'env', 'role', 'clientId']"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
            stripedRows
            :pt="{
                table: {
                    class: 'custom-table',
                },
            }"
        >
            <template #empty> You have no accesses in FAM. </template>
            <template #loading>
                <ProgressSpinner aria-label="Loading" />
            </template>
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

<style>
.my-permissions-table-wrapper {
    margin-top: 3rem;
}

.custom-table {
    table-layout: fixed;
}
</style>
