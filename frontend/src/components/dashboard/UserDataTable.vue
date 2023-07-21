<template>
    <div class="p-access-table">
        <div class="p-table-header">
            <h3>{{ selectedApplicationDisplayText }} users</h3>
            <span>
                This table shows all the users in
                {{ selectedApplicationDisplayText }} and their permissions
                levels
            </span>
        </div>

        <span class="p-input-icon-right">
            <i class="pi pi-search" />
            <InputText class="dash-search" v-model="filters['global'].value" />
        </span>

        <DataTable
            v-model:filters="filters"
            :value="props.userRoleAssignments"
            paginator
            :rows="5"
            :rowsPerPageOptions="[5, 10, 15, 20, 50, 100]"
            dataKey="id"
            filterDisplay="menu"
            :loading="props.loading"
            :globalFilterFields="[
                'user.user_name',
                'role.parent_role.role_name',
                'role.role_name',
                'role.client_number.forest_client_number',
            ]"
            paginatorTemplate="RowsPerPageDropdown CurrentPageReport PrevPageLink NextPageLink"
            currentPageReportTemplate="{currentPage} of {totalPages} pages"
        >
            <template #empty> No application selected. </template>
            <template #loading> Loading customers data. Please wait. </template>
            <Column header="User name" sortable field="user.user_name">
                <template #body="{ data }">
                    <Icon icon="AvatarFilledIcon" medium />
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

<script setup lang="ts">
import { ref } from 'vue';
import type { PropType } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
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

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.p-input-icon-right {
    width: 100%;
    z-index: 1;

    &:deep(.p-inputtext) {
        border-bottom: none;
        width: 100%;
        height: 32px;
        border: none;
    }
}

:deep(.p-datatable .p-sortable-column .p-sortable-column-icon) {
    display: none;
}

.p-datatable-header {
    padding: 0px !important;
}
</style>
