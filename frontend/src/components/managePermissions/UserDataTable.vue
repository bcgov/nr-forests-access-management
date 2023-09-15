<script setup lang="ts">
import { reactive, ref } from 'vue';
import IconCapitol from '@/components/common/IconCapitol.vue';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { IconSize } from '@/enum/IconEnum';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';
import type { PropType } from 'vue';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';

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
    },
    isApplicationSelected: {
        type: Boolean,
        required: true,
        default: false,
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

const emit = defineEmits<{
    (
        e: 'deleteUserRoleAssignment',
        item: FamApplicationUserRoleAssignmentGet
    ): void;
}>();

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
            <p>
                Are you sure you want to remove
                <strong>{{ confirmDeleteData.role }}</strong> access to
                <strong>{{ confirmDeleteData.userName }}</strong> in
                <strong>{{ selectedApplicationDisplayText }}</strong>
            </p>
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <span class="custom-data-table-bg-layer"></span>
            <div v-if="!props.isApplicationSelected" class="no-app-selected">
                <IconCapitol />
                <p class="no-app-selected-title" no-app-selected>
                    Nothing to show yet!
                </p>
                <p class="no-app-selected-text">
                    Choose an application to show a list of users with access to it.
                </p>
                <p class="no-app-selected-text"> The list will display here.</p>
            </div>
            <div class="custom-data-table" v-else>
                <div class="custom-data-table-header">
                    <h3>{{ selectedApplicationDisplayText }} users</h3>
                    <span>
                        This table shows all the users in
                        {{ selectedApplicationDisplayText }} and their permissions
                        levels
                    </span>
                </div>
                <span class="p-input-icon-right">
                    <Icon icon="search" :size="IconSize.small" />
                    <InputText
                        id="dashboardSearch"
                        class="dash-search"
                        v-model="filters['global'].value"
                    />
                </span>

                <DataTable
                    v-model:filters="filters"
                    :value="props.userRoleAssignments"
                    paginator
                    :rows="5"
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
                    <Column header="User name" sortable field="user.user_name">
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
                        field="firstName"
                        header="First name"
                        sortable
                    ></Column>
                    <Column
                        field="lastName"
                        header="Last name"
                        sortable
                    ></Column>
                    <Column
                        field="email"
                        header="Email"
                        sortable
                    ></Column>
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
                    <Column
                        header="Action"
                    >
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
                                <Icon icon="trash-can" :size="IconSize.small"/>
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
    margin-top: 2rem;
    padding-top: 1rem;
}

.custom-data-table-bg-layer {
    position: absolute;
    left: 0;
    right: 0;
    width: 100%;
    min-height: calc(100vh - 13.5rem);
    border-radius: 0.25rem;
    background: $light-layer-one;
    z-index: -1;
}

.btn-icon {
    padding: 0.4rem !important;
    margin-right: 0.5rem;
}

.btn-icon:disabled {
    border: none;
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

.custom-data-table {
    margin-top: 2.5rem;
    margin-bottom: 2.5rem;
    background: transparent;
    border-radius: 0.25rem 0.25rem 0 0;
    border: 0.125rem solid $light-border-subtle-00;
}


// update primevue style but only for FAM
.p-input-icon-right {
    width: 100%;
    z-index: 1;

    &:deep(.p-inputtext) {
        border-bottom: none;
        width: 100%;
        height: 2rem;
        border: none;
    }
}
:deep(.p-datatable .p-sortable-column .p-sortable-column-icon) {
    display: none;
}

/// ----------- no application selected
.no-app-selected {
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 20rem);
    margin: 0 25rem;

    svg {
        width: 3rem;
        height: 3rem;
    }
}

.no-app-selected-title {
    padding-top: 1rem;
    font-size: 1rem;
    font-weight: 700;
}

.no-app-selected-text {
    font-size: 0.875rem;
    color: $light-text-secondary;
    margin-bottom: 0 !important;
}

@media (min-device-width: 1920px) {
    .no-app-selected {
        margin: 0 40.5rem;
    }

    .custom-data-table-bg-layer {
        min-height: calc(100vh - 19.9rem);
    }
}
</style>
