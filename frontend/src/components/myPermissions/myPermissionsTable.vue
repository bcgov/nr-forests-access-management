<script setup lang="ts">
import { ref, shallowRef, type PropType, onMounted, computed } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import InputText from 'primevue/inputtext';
import { IconSize } from '@/enum/IconEnum';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';
import { isLoading } from '@/store/LoadingState';

import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import FamLoginUserState from '@/store/FamLoginUserState';
import DataTableHeader from '../managePermissions/table/DataTableHeader.vue';

const myPermissiosFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
    'application.description': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'application.env': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'application.roles.name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    }
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
                'application.description',
                'application.env',
                'application.roles.name',
            ]"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
            stripedRows
        >
            <template #empty> You have no accesses in FAM. </template>
            <template #loading> Loading permissions data. Please wait. </template>
            <Column
                header="Application"
                field="application.description"
                sortable
            >
                <template #body="{ data }">
                    <span>
                        {{ data.application.name }}
                    </span>
                </template>
            </Column>
            <Column
                field="application.env"
                header="Environment"
                sortable
            ></Column>
            <Column
                header="Client ID"
                sortable
            >
            </Column>
            <Column
                header="Role"
                field="application.roles.name"
                sortable
            >
                <template #body="{ data }">
                    {{ data.application.roles.name }}
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<style>
.my-permissions-table-wrapper {
    margin: 3rem -2.5rem -2.5rem;
}
</style>