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
    selectedApplicationDisplayText: {
        type: String,
        requried: true,
    }
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
    console.log(assignment)
    confirmDeleteData.role = assignment.role.role_name;
    confirmDeleteData.userName = assignment.user.user_name;
    confirm.require({
        group: 'deleteAssignment',
        header: 'Remove Access',
        rejectLabel: 'Cancel',
        acceptLabel: 'Remove',
        acceptClass: 'p-button-danger',
        accept: () => {
            console.log('test', assignment)
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
            <DataTableHeader />
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
                    field="role.client_number.forest_client_number"
                    header="Application"
                    sortable
                ></Column>
                <Column
                    field="role.client_numbe.frorest_client_number"
                    header="Environment"
                    sortable
                ></Column>
                <Column field="role.role_name" header="Role" sortable>
                    <template #body="{ data }">
                        Admin
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

.data-table-container {
    z-index: -1;
}

.custom-data-table {
    background: transparent;
    border-radius: 0 0.25rem 0.25rem 0.25rem;
    border: 0.0625rem solid $light-border-subtle-00;
}

.custom-data-table-header {
    padding: 1rem 1rem 1.5rem;
    background-color: $light-layer-two;
    h3 {
        @extend %heading-03;
        margin: 0;
        padding: 0;
    }

    span {
        @extend %body-compact-01;
        margin: 0;
        padding: 0;
        color: $light-text-secondary;
    }
}

.search-container {
    display: flex;
}

.btn-add-user {
    width: 16rem;
    z-index: 2;
    border-radius: 0rem;
}

.dash-search {
    border-radius: 0 0 0 0;
}

.btn-icon {
    padding: 0.4rem !important;
    margin-right: 0.5rem;
}

.btn-icon:disabled {
    border: none;
}

// update primevue style but only for FAM
.p-input-icon-left {
    z-index: 1;
    flex-grow: 1;

    svg {
        top: 52%;
    }

    &:deep(.p-inputtext) {
        width: 100%;
        border-bottom: 0.125rem solid transparent;
    }

    &:deep(.p-inputtext:hover) {
        border-bottom: 0.125rem solid transparent;
    }
}
:deep(.p-datatable .p-sortable-column .p-sortable-column-icon) {
    display: none;
}

//------ media queries

@media (max-width: 390px) {
    .data-table-container {
        margin: 0;
        padding: 0;
    }
}

@media (min-width: 768px) {
    .data-table-container {
        margin: 0;
        padding: 0;
    }

    .no-app-selected {
        margin: 0 14rem;
    }
}

@media (min-width: 1280px) {
    .no-app-selected {
        margin: 0 25rem;
    }
}

@media (min-width: 1536px) {
    .no-app-selected {
        margin: 0 33rem;
    }
}

@media (min-width: 1920px) {
    .no-app-selected {
        margin: 0 43.3rem;
        width: auto;
    }
}
</style>
