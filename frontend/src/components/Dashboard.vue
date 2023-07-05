<script setup lang="ts">
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import ConfirmDialog from 'primevue/confirmdialog';
import Button from '../components/common/Button.vue';
import InputText from 'primevue/inputtext';
import { useConfirm } from "primevue/useconfirm";
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import { computed, onMounted, ref } from 'vue';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    setSelectedApplication,
    selectedApplicationDisplayText,
} from '@/store/ApplicationState';
import router from '@/router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { FilterMatchMode } from 'primevue/api';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-api/dist/model/fam-application-user-role-assignment-get';

const deleteSuccessMsg = ref<string>('')
const successMsgVisible = ref(false)

const confirm = useConfirm();
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const loading = ref<boolean>(false);
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
const userRoleAssignments = ref<FamApplicationUserRoleAssignmentGet[]>();
onMounted(async () => {
    // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
    try {
        loading.value = true;
        applicationsUserAdministers.value = (
            await applicationsApi.getApplications()
            ).data;
        } catch (error: any) {
        return Promise.reject(error);
    } finally {
        loading.value = false;
    }

    if (isApplicationSelected) {
        getAccessList();
    }
});
const filteredOptions = computed(() => {
    return applicationsUserAdministers.value;
});

const selectApplication = (e: DropdownChangeEvent) => {
    setSelectedApplication(e.value ? JSON.stringify(e.value) : null);
    if (isApplicationSelected) {
        getAccessList();
    }
};

async function getAccessList() {
    try {
        loading.value = true;
        const list = (
            await applicationsApi.getFamApplicationUserRoleAssignment(
                selectedApplication.value!.application_id
            )
        ).data;
        userRoleAssignments.value = list.sort((first, second) => {
            const nameCompare = first.user.user_name.localeCompare(
                second.user.user_name
            );
            if (nameCompare != 0) return nameCompare;
            const roleCompare = first.role.role_name.localeCompare(
                second.role.role_name
            );
            return roleCompare;
        });
    } catch (error: unknown) {
        router.push('/dashboard');
        return Promise.reject(error);
    } finally {
        loading.value = false;
    }
}

async function tryDelete(assignment: FamApplicationUserRoleAssignmentGet, applicationName: string ) {
    let msg = `Are you sure you want to remove <strong>${assignment.role.role_name}</strong> access to <strong>${assignment.user.user_name}</strong> in <strong>${applicationName}</strong>`;
    successMsgVisible.value = false
    confirm.require({
        group: 'templating',
        message: msg,
        icon: 'none',
        header: 'Remove Access',
        rejectLabel: 'Remove',
        acceptLabel: 'Cancel',
        reject: () => {
            try {
                userRoleAssignmentApi.deleteUserRoleAssignment(
                    assignment.user_role_xref_id
                    );
                    userRoleAssignments.value =
                    userRoleAssignments.value!.filter((a) => {
                                return !(
                                    a.user_role_xref_id ==
                                    assignment.user_role_xref_id
                                    );
                    });
                deleteSuccessMsg.value = ''
            } finally {
                    deleteSuccessMsg.value = `You removed ${assignment.role.role_name} access to ${assignment.user.user_name}`
                    successMsgVisible.value = true
            }
        },        
    });
};
</script>

<template>
    <ConfirmDialog group="templating">
        <template #message="slotProps">
            <p v-html="slotProps.message.message"></p>
        </template>
    </ConfirmDialog>

    <div class="row">
        <div class="col-6">
            <PageTitle title="Dashboard" subtitle="Manage permissions" />
        </div>
        <div class="col-6">
            <Button
                v-if="isApplicationSelected"
                class="dashboard-button"
                label="Grant new access"
                @click="router.push('/grant')"
                ><Icon icon="AddIcon" medium class="icon-size-1"
            /></Button>
        </div>
    </div>
    <div class="page-body">
        <div class="row">
            <div class="col-12">
                <form
                    id="selectApplicationForm"
                    class="form-container dashboard-form"
                >
                    <div class="form-group">
                        <div class="row">
                            <label
                                >Select an application you would like to grant
                                access</label
                            >
                            <Dropdown
                                v-model="selectedApplication"
                                @change="selectApplication"
                                :options="filteredOptions"
                                optionLabel="application_description"
                                placeholder="Choose an option"
                                class="application-dropdown"
                            />
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <NotificationMessage
        v-if="successMsgVisible"
        severity="success"
        :msgText="deleteSuccessMsg" 
        icon="CheckIcon"
    />
    <div class="row h-auto" v-if="isApplicationSelected">
        <div class="col-12">
            <div class="p-access-table">
                <div class="p-table-header">
                    <h3>{{ selectedApplicationDisplayText }} users</h3>
                    <span>
                        This table shows all the users in
                        {{ selectedApplicationDisplayText }} and their
                        permissions levels
                    </span>
                </div>

                <span class="p-input-icon-right">
                    <i class="pi pi-search" />
                    <InputText
                        class="dash-search"
                        v-model="filters['global'].value"
                    />
                </span>

                <DataTable
                    v-model:filters="filters"
                    :value="userRoleAssignments"
                    paginator
                    :rows="5"
                    :rowsPerPageOptions="[5, 10, 15, 20, 50, 100]"
                    dataKey="id"
                    filterDisplay="menu"
                    :loading="loading"
                    :globalFilterFields="[
                        'user.user_name',
                        'role.parent_role.role_name',
                        'role.role_name',
                        'role.client_number.forest_client_number',
                    ]"
                    paginatorTemplate="RowsPerPageDropdown CurrentPageReport PrevPageLink NextPageLink"
                    currentPageReportTemplate="{currentPage} of {totalPages} pages"
                >
                    <!-- This is where we set the pagination
                            <template #paginatorstart="{slotProps: props}">
                            {{ slotProps?.RowsPerPageDropdown }}
                        </template> -->

                    <template #empty> No application selected. </template>
                    <template #loading>
                        Loading customers data. Please wait.
                    </template>
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
                                @click="tryDelete(data, selectedApplicationDisplayText)"
                            >
                                <span class="remove-action">Remove</span>
                            </button>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';

.application-dropdown {
    width: 304px;
    padding: 0px;
}

.p-input-icon-right {
    width: 100%;

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
.dashboard-button {
    width: 235px;
    float: right;
}
.p-datatable-header {
    padding: 0px !important;
}

.span-icon {
    margin-left: 15px;
}
// =======
// .access-table {
//     margin-top: 100px;
//     background: #ffffff;
//     border-radius: 4px 4px 0px 0px;
//     border: 2px solid #dfdfe1;
// }
// .table-header {
//     padding: 16px 16px 24px;
// >>>>>>> 5dd49b0 (fix/653-update-notifications-and-modals: Added dialog and success message to dashboard)
// }

.remove-action {
    color: $text-error;
}
</style>
