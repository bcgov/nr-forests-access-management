<script setup lang="ts">
import { computed, reactive, ref, type PropType } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';

import { IconSize } from '@/enum/IconEnum';
import { routeItems } from '@/router/routeItem';
import Button from '@/components/common/Button.vue';
import ConfirmDialogtext from '@/components/managePermissions/ConfirmDialogText.vue';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import NewUserTag from '@/components/common/NewUserTag.vue';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';

import type { FamAppAdminGetResponse } from 'fam-admin-mgmt-api/model';

type emit = (e: 'deleteAppAdmin', item: FamAppAdminGetResponse) => void;

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    applicationAdmins: {
        type: [Array] as PropType<FamAppAdminGetResponse[] | undefined>,
        required: true,
    },
    newAppAdminId: {
        type: Array,
        default: [],
    },
});

const applicationAdmins = computed(() => {
    if (props.newAppAdminId.length === 0) {
        return props.applicationAdmins;
    } else {
        return props.applicationAdmins?.slice().sort((a, b) => {
            const aIsNew = props.newAppAdminId.includes(a.application_admin_id);
            const bIsNew = props.newAppAdminId.includes(b.application_admin_id);

            if (aIsNew && !bIsNew) {
                return -1;
            } else if (!aIsNew && bIsNew) {
                return 1;
            } else {
                return 0;
            }
        });
    }
});

const adminFilters = ref({
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

const confirm = useConfirm();

const emit = defineEmits<emit>();

const confirmDeleteData = reactive({
    adminName: '',
    role: 'ADMIN',
});

const adminSearchChange = (newvalue: string) => {
    adminFilters.value.global.value = newvalue;
};

const deleteAdmin = (admin: FamAppAdminGetResponse) => {
    confirmDeleteData.adminName = admin.user.user_name;
    confirm.require({
        group: 'deleteAdmin',
        header: 'Remove Access',
        rejectLabel: 'Cancel',
        acceptLabel: 'Remove',
        accept: () => {
            emit('deleteAppAdmin', admin);
        },
    });
};

const isNewAppAdminAccess = (applicationAdminId: number | null) => {
    const test = props.newAppAdminId.includes(applicationAdminId);
    console.log(test);
    return test;
};

const highlightNewAppAdminAccesRow = (rowData: any) => {
    if(isNewAppAdminAccess(rowData.application_admin_id)) {
        return {
            'background-color': '#C2E0FF',
            'box-shadow': 'inset 0 0 0 0.063rem #85C2FF'
        }
    }
}
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
                btnLabel="Add application admin"
                :btnRoute="routeItems.grantAppAdmin.path"
                :filter="adminFilters['global'].value"
                @change="adminSearchChange"
            />
            <DataTable
                v-model:filters="adminFilters"
                :value="applicationAdmins"
                paginator
                :rows="50"
                :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
                filterDisplay="menu"
                :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'application.application_name',
                    'user.user_type.description',
                    'role.role_name',
                    'application.app_environment',
                ]"
                :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
                stripedRows
                :rowStyle="highlightNewAppAdminAccesRow"
            >
                <template #empty> No user found. </template>
                <template #loading> Loading users data. Please wait. </template>
                <Column header="User Name" sortable field="user.user_name">
                    <template #body="{ data }">
                        <NewUserTag
                            v-if="
                                isNewAppAdminAccess(
                                    data.application_admin_id
                                ) && props.newAppAdminId.length > 0
                            "
                        />
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
                    field="application.application_name"
                    header="Application"
                    sortable
                ></Column>
                <Column
                    field="application.app_environment"
                    header="Environment"
                    sortable
                ></Column>
                <Column field="role.role_name" header="Role" sortable>
                    <template #body="{ data }"> Admin </template></Column
                >
                <Column header="Action">
                    <template #body="{ data }">
                        <!-- Hidden until functionality is available
                            <button
                                class="btn btn-icon"
                            >
                                <Icon icon="edit" :size="IconSize.small"/>
                            </button> -->
                        <button
                            title="Delete application admin"
                            class="btn btn-icon"
                            @click="deleteAdmin(data)"
                        >
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
