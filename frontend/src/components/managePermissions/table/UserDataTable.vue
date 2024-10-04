<script setup lang="ts">
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import ConfirmDialog from 'primevue/confirmdialog';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';
import { useConfirm } from 'primevue/useconfirm';
import { computed, reactive, ref, type PropType } from 'vue';

import NewUserTag from '@/components/common/NewUserTag.vue';
import ConfirmDialogtext from '@/components/managePermissions/ConfirmDialogText.vue';
import DataTableHeader from '@/components/managePermissions/table/DataTableHeader.vue';
import { IconSize } from '@/enum/IconEnum';
import { hashRouter } from '@/router';
import { routeItems } from '@/router/routeItem';
import { isNewAccess } from '@/services/utils';
import { selectedApplicationId } from '@/store/ApplicationState';
import {
    NEW_ACCESS_STYLE_IN_TABLE,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from '@/store/Constants';
import type { FamApplicationUserRoleAssignmentGetSchema } from 'fam-app-acsctl-api';


type emit = (
    e: 'deleteUserRoleAssignment',
    item: FamApplicationUserRoleAssignmentGetSchema
) => void;

const confirm = useConfirm();
const emit = defineEmits<emit>();

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    userRoleAssignments: {
        type: [Array] as PropType<
            FamApplicationUserRoleAssignmentGetSchema[] | undefined
        >,
        required: true,
    },
    newIds: {
        type: String,
        default: '',
    },
});

const newUserAccessIds = computed(() => {
    return props.newIds.split(',');
});

const userRoleAssignmentsFilters = ref({
    global: { value: '', matchMode: FilterMatchMode.CONTAINS },
});

const userSearchChange = (newValue: string) => {
    userRoleAssignmentsFilters.value.global.value = newValue;
};

const confirmDeleteData = reactive({
    userName: '',
    role: '',
});

function deleteAssignment(assignment: FamApplicationUserRoleAssignmentGetSchema) {
    confirmDeleteData.role = assignment.role.role_name;
    confirmDeleteData.userName = assignment.user.user_name;
    confirm.require({
        group: 'deleteAssignment',
        header: 'Remove Access',
        rejectLabel: 'Cancel',
        acceptLabel: 'Remove',
        accept: () => {
            emit('deleteUserRoleAssignment', assignment);
        },
    });
}

const navigateToUserDetails = (userId: string) => {
    hashRouter.push({
        name: routeItems.userDetails.name,
        params: {
            applicationId: selectedApplicationId.value,
            userId,
        }
    });
}

const highlightNewUserAccessRow = (rowData: any) => {
    if (isNewAccess(newUserAccessIds.value, rowData.user_role_xref_id)) {
        return NEW_ACCESS_STYLE_IN_TABLE;
    }
};
</script>

<template>
    <ConfirmDialog group="deleteAssignment">
        <template #message>
            <ConfirmDialogtext :role="confirmDeleteData.role" :userName="confirmDeleteData.userName" />
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <div class="custom-data-table">
            <DataTableHeader btnLabel="Add user permission" :btnRoute="routeItems.grantUserPermission.path"
                :filter="userRoleAssignmentsFilters['global'].value" @change="userSearchChange" />
            <DataTable v-model:filters="userRoleAssignmentsFilters" :value="userRoleAssignments" paginator :rows="50"
                :rowsPerPageOptions="TABLE_ROWS_PER_PAGE" filterDisplay="menu" :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'role.parent_role.role_name',
                    'user.user_type.description',
                    'user.first_name',
                    'user.last_name',
                    'user.email',
                    'role.role_name',
                    'role.forest_client.forest_client_number',
                ]" :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE" stripedRows
                :rowStyle="highlightNewUserAccessRow">
                <template #empty> No user found. </template>
                <template #loading>
                    <ProgressSpinner aria-label="Loading" />
                </template>
                <Column header="User Name" sortable field="user.user_name">
                    <template #body="{ data }">
                        <NewUserTag v-if="
                            isNewAccess(
                                newUserAccessIds,
                                data.user_role_xref_id
                            )
                        " />
                        <span>
                            {{ data.user.user_name }}
                        </span>
                    </template>
                </Column>
                <Column field="user.user_type.description" header="Domain" sortable></Column>
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
                <Column field="role.forest_client.forest_client_number" header="Client Number" sortable></Column>
                <Column field="role.role_name" header="Role" sortable>
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

                        <button title="Delete user" class="btn btn-icon" @click="deleteAssignment(data)">
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
