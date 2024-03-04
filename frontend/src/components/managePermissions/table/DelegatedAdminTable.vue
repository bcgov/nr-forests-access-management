<script setup lang="ts">
import { ref, type PropType } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

import { routeItems } from '@/router/routeItem';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import type { FamAccessControlPrivilegeGetResponse } from 'fam-admin-mgmt-api/model';

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    delegatedAdmins: {
        type: [Array] as PropType<
            FamAccessControlPrivilegeGetResponse[] | undefined
        >,
        required: true,
    },
});

const delegatedAdminFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
    'user.user_name': { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    'user.user_type.description': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.parent_role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.client_number.forest_client_number': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
});

const delegatedAdminSearchChange = (newvalue: string) => {
    delegatedAdminFilters.value.global.value = newvalue;
};
</script>

<template>
    <!-- Hidden until functionality is available
    <ConfirmDialog group="deleteAdmin">
        <template #message>
            <ConfirmDialogtext
                :userName=""
                :role=""
            />
        </template>
    </ConfirmDialog> -->
    <div class="data-table-container">
        <div class="custom-data-table">
            <DataTableHeader
                btnLabel="Create delegated admin"
                :btnRoute="routeItems.grantDelegatedAdmin.path"
                :filter="delegatedAdminFilters['global'].value"
                @change="delegatedAdminSearchChange"
            />
            <DataTable
                v-model:filters="delegatedAdminFilters"
                :value="props.delegatedAdmins"
                paginator
                :rows="50"
                :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
                filterDisplay="menu"
                :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'user.user_type.description',
                    'role.role_name',
                    'role.parent_role.role_name',
                    'role.client_number.forest_client_number',
                ]"
                :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
                stripedRows
            >
                <template #empty> No user found. </template>
                <template #loading> Loading users data. Please wait. </template>
                <Column
                    header="User Name"
                    field="user.user_name"
                    sortable
                >
                    <template #body="{ data }">
                        <span>
                            {{ data.user.user_name }}
                        </span>
                    </template>
                </Column>
                <Column
                    field="user.user_type.description"
                    header="Domain"
                    sortable
                ></Column>
                <Column
                    field="role.client_number.forest_client_number"
                    header="Client ID"
                    sortable
                >
                </Column>
                <Column
                    header="Role Enabled To Assign"
                    sortable
                >
                    <template #body="{ data }">
                        {{
                            data.role.parent_role
                                ? data.role.parent_role.role_name
                                : data.role.role_name
                        }}
                    </template>
                </Column>
                <Column header="Action">
                    <template #body="{ data }">
                        <!-- Hidden until functionality is available
                            <button
                                class="btn btn-icon"
                            >
                                <Icon icon="edit" :size="IconSize.small"/>
                            </button> -->
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
</style>
