<script setup lang="ts">
import { ref } from 'vue';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import { FilterMatchMode } from 'primevue/api';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';
import { isLoading } from '@/store/LoadingState';

import FamLoginUserState from '@/store/FamLoginUserState';

const myPermissiosFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
    'application': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'env': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'clientId': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'adminRole': {
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
        <DataTableHeader
            :hasHeader="false"
            input-placeholder="Search for application, environment, client IDs, company name, role, status, and more"
            @change="myPermissionsSearchChange"
            :filter="myPermissiosFilters['global'].value"
        />
        <DataTable
            class="custom-data-table"
            v-model:filters="myPermissiosFilters"
            :value="FamLoginUserState.getMyCachedPermissions()"
            paginator
            :rows="50"
            :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
            filterDisplay="menu"
            :loading="isLoading()"
            :globalFilterFields="[
                'application',
                'env',
                'adminRole',
                'clientId',
            ]"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
            stripedRows
        >
            <template #empty> You have no accesses in FAM. </template>
            <template #loading>
                Loading permissions data. Please wait.
            </template>
            <Column
                header="Application"
                field="application"
                sortable
            >
                <template #body="{ data }">
                    <span>
                        {{ data.application }}
                    </span>
                </template>
            </Column>
            <Column
                field="env"
                header="Environment"
                sortable
            ></Column>
            <Column
                field="clientId"
                header="Client ID"
                sortable
            >
            </Column>
            <Column
                header="Role"
                field="adminRole"
                sortable
            >
                <template #body="{ data }">
                    {{
                        data.adminRole === 'Delegated Admin'
                            ? `${data.adminRole}, ${data.role}`
                            : data.adminRole
                    }}
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<style>
.my-permissions-table-wrapper {
    margin: 3rem -2.5rem -2.5rem;
}
@media (max-width: 768px) {
    .my-permissions-table-wrapper {
        margin: 3rem 0;
    }
}
</style>
