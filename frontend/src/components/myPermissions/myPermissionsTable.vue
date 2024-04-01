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

const delegatedAdminFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
    'application.description': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'application.env': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'roles.name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    }
});

const delegatedAdminSearchChange = (newvalue: string) => {
    delegatedAdminFilters.value.global.value = newvalue;
};
</script>

<template>
    <div class="p-input-icon-left">
        <Icon
            icon="search"
            :size="IconSize.small"
        />
        <InputText
            id="dashboardSearch"
            class="dash-search"
            placeholder="Search by keyword"
            v-model="delegatedAdminFilters['global'].value"
        />
    </div>
    <DataTable
        v-model:filters="delegatedAdminFilters"
        :value="FamLoginUserState.getMyCachedPermissions()"
        paginator
        :rows="50"
        :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
        filterDisplay="menu"
        :loading="isLoading()"
        :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
        :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
        stripedRows
    >
        <template #empty> No user found. </template>
        <template #loading> Loading users data. Please wait. </template>
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
            sortable
        >
            <template #body="{ data }">
                {{ data.roles.name }}
            </template>
        </Column>
    </DataTable>
</template>
