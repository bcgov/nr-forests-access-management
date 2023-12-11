<script setup lang="ts">
import { reactive, ref } from 'vue';
import type { PropType } from 'vue';

import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';

import router from '@/router';
import { IconSize } from '@/enum/IconEnum';
import IconCapitol from '@/components/common/IconCapitol.vue';
import Button from '@/components/common/Button.vue';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';

type emit = (
    e: 'deleteUserRoleAssignment',
    item: FamApplicationUserRoleAssignmentGet
) => void;

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

const confirm = useConfirm();

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
            <p>
                Are you sure you want to remove
                <strong>{{ confirmDeleteData.role }}</strong> access to
                <strong>{{ confirmDeleteData.userName }}</strong> in
                <strong>{{ selectedApplicationDisplayText }}</strong>
            </p>
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <div v-if="!props.isApplicationSelected" class="no-app-selected">
            <IconCapitol />
            <p class="no-app-selected-title" no-app-selected>
                Nothing to show yet!
            </p>
            <p class="no-app-selected-text">
                Choose an application to show a list of users with access to it.
                The list will display here.
            </p>
        </div>
            <TabView v-else >
                <TabPanel header="Users">
                    <template #header >
                        <Icon
                            icon="user"
                            :size="IconSize.small"
                        />
                    </template>
                    <div class="custom-data-table">
                        <div class="custom-data-table-header">
                            <h3>{{ selectedApplicationDisplayText }} users</h3>
                            <span>
                                This table shows all the users in
                                {{ selectedApplicationDisplayText }} and their permissions
                                levels
                            </span>
                        </div>
                        <div class="search-container">
                            <Button
                                class="btn-add-user"
                                label="Add user permission"
                                @click="router.push('/grant')"
                            >
                                <Icon icon="add" :size="IconSize.small" />
                            </Button>
                            <span class="p-input-icon-left">
                                <Icon icon="search" :size="IconSize.small" />
                                <InputText
                                    id="dashboardSearch"
                                    class="dash-search"
                                    placeholder="Search by keyword"
                                    v-model="filters['global'].value"
                                />
                            </span>
                        </div>

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
                </TabPanel>
                <TabPanel
                    header="Delegated admins"
                    :disabled="true"
                >
                    <template #header >
                        <Icon
                            icon="enterprise"
                            :size="IconSize.small"
                        />
                    </template>
                </TabPanel>
            </TabView>

    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.data-table-container {
    margin: 2rem 0.05rem 0.05rem;
    z-index: -1;
}

.custom-data-table {
    margin: 0 2.5rem 0;
    border-radius: 0 0.25rem 0.25rem 0.25rem;
    border: 1px solid $light-border-subtle-00;
    margin-top: 0;
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

/// ----------- no application selected
.no-app-selected {
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 21.745rem);
    min-height: 12.5rem;
    margin: 0 5rem;

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

//------ media queries

@media (max-width: 390px) {
    .data-table-container {
        margin: 0;
        padding: 0;
    }
}

@media (min-width: 768px) {
    .data-table-container {
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
