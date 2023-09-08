<script setup lang="ts">
import { IconSize } from '@/enum/IconEnum';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import ConfirmDialog from 'primevue/confirmdialog';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useConfirm } from 'primevue/useconfirm';
import type { PropType } from 'vue';
import { reactive, ref } from 'vue';

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

    <div class="custom-data-table">
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
            currentPageReportTemplate="{currentPage} of {totalPages} pages"
        >
            <template #empty> No user found. </template>
            <template #loading> Loading users data. Please wait. </template>
            <Column header="User name" sortable field="user.user_name">
                <template #body="{ data }">
                    <Icon icon="user--avatar--filled" :size="IconSize.medium" />
                    <span class="span-icon">
                        {{ data.user.user_name }}
                    </span>
                </template>
            </Column>
            <Column
                field="user.user_type.description"
                header="Domain"
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
                field="role.client_number.forest_client_number"
                header="Forest Client ID"
                sortable
            ></Column>
            <Column>
                <template #body="{ data }">
                    <button
                        class="btn btn-icon"
                        @click="deleteAssignment(data)"
                    >
                        <span class="remove-action">Remove</span>
                    </button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.custom-data-table {
    margin-top: 4.9375rem;
    background: transparent;
    border-radius: 0.25rem 0.25rem 0 0;
    border: 0.125rem solid $light-border-subtle-00;
}

.custom-data-table-header {
    padding: 1rem 1rem 1.5rem;
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

.span-icon {
    margin-left: 0.9375rem;
}

.remove-action {
    color: $light-text-error;
}
</style>
