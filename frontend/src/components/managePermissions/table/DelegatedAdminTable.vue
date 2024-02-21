<script setup lang="ts">
import { reactive, ref, type PropType } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ConfirmDialog from 'primevue/confirmdialog';

import { IconSize } from '@/enum/IconEnum';
import { routeItems } from '@/router/routeItem';
import Button from '@/components/common/Button.vue';
import ConfirmDialogtext from '@/components/managePermissions/ConfirmDialogText.vue';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import type { FamAccessControlPrivilegeGetResponse } from 'fam-admin-mgmt-api/model';

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    delegatedAdmins: {
        type: [Array] as PropType<FamAccessControlPrivilegeGetResponse[] | undefined>,
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
    'application.app_environment': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
});

const confirmDeleteData = reactive({
    adminName: '',
    role: ''
});

const adminSearchChange = (newvalue: string) => {
    delegatedAdminFilters.value.global.value = newvalue;
};
</script>

<template>
    <ConfirmDialog group="deleteAdmin">
        <template #message>
            <ConfirmDialogtext
                :userName="confirmDeleteData.adminName"
                :role="confirmDeleteData.role"
            />
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <div class="custom-data-table">
            <DataTableHeader
                btnLabel="Create delegated admin"
                :btnRoute="routeItems.grantAppAdmin.path"
                :filter="delegatedAdminFilters['global'].value"
                @change="adminSearchChange"
            />
            <DataTable
                v-model:filters="delegatedAdminFilters"
                :value="props.delegatedAdmins"
                paginator
                :rows="50"
                :rowsPerPageOptions="[5, 10, 15, 20, 50, 100]"
                filterDisplay="menu"
                :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'application.application_name',
                    'user.user_type.description',
                    'role.role_name.role_name',
                    'application.app_environment',
                ]"
                paginatorTemplate="RowsPerPageDropdown CurrentPageReport PrevPageLink NextPageLink"
                currentPageReportTemplate="{first} - {last} of {totalRecords} items"
                stripedRows
            >
                <template #empty> No user found. </template>
                <template #loading> Loading users data. Please wait. </template>
                <Column header="User Name" sortable field="user.user_name">
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
                    field="application.app_environment"
                    header="Client ID"
                    sortable
                >
                    <template #body="{ data }"> - </template>
                </Column>
                <Column
                    field="role.role_name"
                    header="Role Enabled To Assign"
                    sortable
                >
                    <template #body="{ data }"> reviewer </template>
                </Column>
                <Column header="Action">
                    <template #body="{ data }">
                        <!-- Hidden until functionality is available
                            <button
                                class="btn btn-icon"
                            >
                                <Icon icon="edit" :size="IconSize.small"/>
                            </button> -->
                        <button class="btn btn-icon">
                            <Icon icon="trash-can" :size="IconSize.small" />
                        </button>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
</style>
