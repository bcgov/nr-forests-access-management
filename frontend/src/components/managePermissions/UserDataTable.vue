<script setup lang="ts">
import { reactive, ref } from 'vue';
import type { PropType } from 'vue';

import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';

import { IconSize } from '@/enum/IconEnum';
import Button from '@/components/common/Button.vue';
import ConfirmDialogtext from '@/components/common/ConfirmDialogText.vue';
import DataTableHeader from '@/components/managePermissions/DataTableHeader.vue';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';

type emit = (
    e: 'deleteUserRoleAssignment',
    item: FamApplicationUserRoleAssignmentGet
) => void;

const confirm = useConfirm();

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    userRoleAssignments: {
        type: [Array] as PropType<
            FamApplicationUserRoleAssignmentGet[] | undefined
        >,
        required: true,
    },
});

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    'user.user_name': { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    'role.parent_role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.client_number.forest_client_number': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
});

const confirmDeleteData = reactive({
    userName: '',
    role: '',
});

const emit = defineEmits<emit>();

function deleteAssignment(assignment: FamApplicationUserRoleAssignmentGet) {
    confirmDeleteData.role = assignment.role.role_name;
    confirmDeleteData.userName = assignment.user.user_name;
    confirm.require({
        group: 'deleteAssignment',
        header: 'Remove Access',
        rejectLabel: 'Cancel',
        acceptLabel: 'Remove',
        acceptClass: 'p-button-danger',
        accept: () => {
            emit('deleteUserRoleAssignment', assignment);
        },
    });
}
</script>

<template>
    <ConfirmDialog group="deleteAssignment">
        <template #message>
            <ConfirmDialogtext
                :role="confirmDeleteData.role"
                :userName="confirmDeleteData.userName"
            />
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <div class="custom-data-table">
            <DataTableHeader
                btnLabel="Add user permission"
                btnRoute="/grant"
            />
            <DataTable
                v-model:filters="filters"
                :value="props.userRoleAssignments"
                paginator
                :rows="50"
                :rowsPerPageOptions="[5, 10, 15, 20, 50, 100]"
                filterDisplay="menu"
                :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'role.parent_role.role_name',
                    'user.user_type.description',
                    'role.role_name',
                    'role.client_number.forest_client_number',
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
                <!-- Hidden until information is available
                    <Column
                        field="firstName"
                        header="First Name"
                        sortable
                    ></Column>
                    <Column
                        field="lastName"
                        header="Last Name"
                        sortable
                    ></Column>
                    <Column
                        field="email"
                        header="Email"
                        sortable
                    ></Column>
                     -->
                <Column
                    field="role.client_number.forest_client_number"
                    header="Client ID"
                    sortable
                ></Column>
                <Column field="role.role_name" header="Role" sortable>
                    <template #body="{ data }">
                        {{
                            data.role.parent_role
                                ? data.role.parent_role.role_name
                                : data.role.role_name
                        }}
                    </template></Column
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
                            class="btn btn-icon"
                            @click="deleteAssignment(data)"
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
