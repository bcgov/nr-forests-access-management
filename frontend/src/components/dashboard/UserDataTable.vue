<script setup lang="ts">
import { ref } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { IconSize } from '@/enum/IconEnum';
import type { PropType } from 'vue';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';

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
</script>

<template>
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
            <InputText class="dash-search" v-model="filters['global'].value" />
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
                        @click="$emit('deleteUserRoleAssignment', data)"
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

.span-icon {
    margin-left: 0.9375rem;
}

.remove-action {
    color: $light-text-error;
}

</style>
