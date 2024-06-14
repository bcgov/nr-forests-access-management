<script setup lang="ts">
import { ref, reactive, computed, type PropType } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';

import { routeItems } from '@/router/routeItem';
import NewUserTag from '@/components/common/NewUserTag.vue';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import { IconSize } from '@/enum/IconEnum';
import type { FamAccessControlPrivilegeGetResponse } from 'fam-admin-mgmt-api/model';

type emit = (
    e: 'deleteDelegatedAdminAssignment',
    item: FamAccessControlPrivilegeGetResponse
) => void;

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
    newDelegatedAdminId: {
        type: Array,
        default: [],
    }
});

const delegatedAdmins = computed(() => {
    if (props.newDelegatedAdminId.length === 0) {
        return props.delegatedAdmins;
    } else {
        return props.delegatedAdmins?.slice().sort((a, b) => {
            const aIsNew = props.newDelegatedAdminId.includes(a.access_control_privilege_id);
            const bIsNew = props.newDelegatedAdminId.includes(b.access_control_privilege_id);

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

const confirm = useConfirm();

const emit = defineEmits<emit>();

const confirmDeleteData = reactive({
    adminName: '',
    role: '',
});

const deleteDelegatedAdmin = (
    delegatedAdmin: FamAccessControlPrivilegeGetResponse
) => {
    confirmDeleteData.adminName = delegatedAdmin.user.user_name;
    confirmDeleteData.role = delegatedAdmin.role.parent_role
        ? delegatedAdmin.role.parent_role.role_name
        : delegatedAdmin.role.role_name;
    confirm.require({
        group: 'deleteDelegatedAdmin',
        header: 'Remove Privilege',
        rejectLabel: 'Cancel',
        acceptLabel: 'Remove',
        accept: () => {
            emit('deleteDelegatedAdminAssignment', delegatedAdmin);
        },
    });
};

const isNewAppAdminAccess = (accessControlPrivilegeId: number | null) => {
    const test = props.newDelegatedAdminId.includes(accessControlPrivilegeId);
    return test;
};

const highlightNewAppAdminAccessRow = (rowData: any) => {
    if(isNewAppAdminAccess(rowData.access_control_privilege_id)) {
        return {
            'background-color': '#C2E0FF',
            'box-shadow': 'inset 0 0 0 0.063rem #85C2FF'
        }
    }
}

</script>

<template>
    <ConfirmDialog group="deleteDelegatedAdmin">
        <template #message>
            <ConfirmDialogText
                :userName="confirmDeleteData.adminName"
                :role="confirmDeleteData.role"
                customMsg="privilege"
            />
        </template>
    </ConfirmDialog>
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
                :value="delegatedAdmins"
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
                :rowStyle="highlightNewAppAdminAccessRow"
            >
                <template #empty> No user found. </template>
                <template #loading> Loading users data. Please wait. </template>
                <Column header="User Name" field="user.user_name" sortable>
                    <template #body="{ data }">
                        <NewUserTag v-if="
                                isNewAppAdminAccess(
                                    data.access_control_privilege_id
                                ) && props.newDelegatedAdminId.length > 0
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
                    field="role.client_number.forest_client_number"
                    header="Client Number"
                    sortable
                >
                </Column>
                <Column
                    header="Role Enabled To Assign"
                    sortable
                    field="role.role_name"
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
                        <button
                            class="btn btn-icon"
                            title="Delete delegated admin"
                            @click="deleteDelegatedAdmin(data)"
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
