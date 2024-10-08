<script setup lang="ts">
import { ref, reactive, computed, type PropType } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';
import { isNewAccess } from '@/services/utils';
import ProgressSpinner from 'primevue/progressspinner';

import { routeItems } from '@/router/routeItem';
import NewUserTag from '@/components/common/NewUserTag.vue';
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
    NEW_ACCESS_STYLE_IN_TABLE,
} from '@/store/Constants';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import { IconSize } from '@/enum/IconEnum';
import type { FamAccessControlPrivilegeGetResponse } from 'fam-admin-mgmt-api/model';
import { navigateToUserDetails } from '@/components/managePermissions/table/utils';
import Icon from '@/components/common/Icon.vue'

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
    newIds: {
        type: String,
        default: '',
    },
});

const newDelegatedAdminIds = computed(() => {
    return props.newIds.split(',');
});

const delegatedAdminFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
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

const highlightNewDelegatedAdminAccessRow = (rowData: any) => {
    if (
        isNewAccess(
            newDelegatedAdminIds.value,
            rowData.access_control_privilege_id
        )
    ) {
        return NEW_ACCESS_STYLE_IN_TABLE;
    }
};
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
                    'user.first_name',
                    'user.last_name',
                    'user.email',
                    'role.parent_role.role_name',
                    'role.client_number.forest_client_number',
                ]"
                :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
                stripedRows
                :rowStyle="highlightNewDelegatedAdminAccessRow"
            >
                <template #empty> No user found. </template>
                <template #loading>
                    <ProgressSpinner aria-label="Loading" />
                </template>
                <Column header="User Name" field="user.user_name" sortable>
                    <template #body="{ data }">
                        <NewUserTag
                            v-if="
                                isNewAccess(
                                    newDelegatedAdminIds,
                                    data.access_control_privilege_id
                                )
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
                <Column field="user.first_name" header="Full Name" sortable>
                    <template #body="{ data }">
                        {{
                            data.user.first_name && data.user.last_name
                                ? data.user.first_name +
                                  ' ' +
                                  data.user.last_name
                                : ''
                        }}
                    </template>
                </Column>
                <Column field="user.email" header="Email" sortable></Column>
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
                        <button title="User permission history" class="btn btn-icon"
                            @click="navigateToUserDetails(data.user_id)">
                            <Icon icon="history" :size="IconSize.small" />
                        </button>

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
