<script setup lang="ts">
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import Button from '../components/common/Button.vue';
import InputText from 'primevue/inputtext';
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
import { useToast } from 'vue-toastification';
import { $vfm } from 'vue-final-modal';

import Dialog from '@/components/dialog/Dialog.vue';
import Add from '../components/icons/Add.vue';

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
        applicationsUserAdministers.value = (
            await applicationsApi.getApplications()
        ).data;
    } catch (error: any) {
        return Promise.reject(error);
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
    }
}

async function tryDelete(assignment: FamApplicationUserRoleAssignmentGet) {
    let msg = `Delete access for user ${assignment.user.user_name} from role ${assignment.role.role_name}`;
    if (assignment.role.client_number) {
        msg += ` for client ${assignment.role.client_number.forest_client_number}`;
    }
    msg += '?';

    $vfm.show({
        component: Dialog,
        bind: {
            title: 'Are you sure?',
            message: msg,
            confirmText: 'Yes, delete',
        },
        on: {
            confirm() {
                // Deletion confirmed.
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
                    useToast().success(
                        `Access deleted for user ${assignment.user.user_name}.`
                    );
                } finally {
                    $vfm.hideAll();
                }
            },
        },
    });
}
</script>

<template>
    <div class="vh-100">
        <div class="row">
            <div class="col-6">
                <h5 class="title">Dashboard</h5>
                <span class="subtitle">Manage permissions</span>
            </div>
            <div class="col-6">
                <Button
                    v-if="isApplicationSelected"
                    style="float: right"
                    class="dashboard-button"
                    label="Grant new access"
                    @click="router.push('/grant')"
                    ><Icon icon="Add" medium class="icon-size-1"
                /></Button>
            </div>
        </div>
        <div class="row vh-20">
            <div class="col-sm-12 col-md-12 col-lg-12">
                <form id="selectApplicationForm" class="form-container">
                    <div class="form-group col-md-5">
                        <label class="label"
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
                </form>
            </div>
        </div>
        <div class="row h-auto" v-if="isApplicationSelected">
            <div class="col-sm-12 col-md-12 col-lg-12">
                <div class="access-table">
                    <div class="table-header">
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
                            class="w-auto"
                            v-model="filters['global'].value"
                        />
                    </span>

                    <DataTable
                        v-model:filters="filters"
                        :value="userRoleAssignments"
                        paginator
                        :rows="10"
                        tableStyle="max-height: 60vh"
                        dataKey="id"
                        filterDisplay="menu"
                        :loading="loading"
                        :globalFilterFields="[
                            'user.user_name',
                            'role.parent_role.role_name',
                            'role.role_name',
                            'role.client_number.forest_client_number',
                        ]"
                        paginatorTemplate="JumpToPageDropdown CurrentPageReport PrevPageLink NextPageLink"
                        currentPageReportTemplate="{first} - {last} of {totalRecords} items {currentPage} of {totalPages} pages"
                    >
                        <template #paginatorstart>
                            <Button type="button" icon="pi pi-refresh" text />
                        </template>
                        <!-- <template #paginatorend>
                            <Button type="button" icon="pi pi-download" text />
                        </template> -->
                        <template #empty> No application selected. </template>
                        <template #loading>
                            Loading customers data. Please wait.
                        </template>
                        <Column
                            header="User name"
                            sortable
                            field="user.user_name"
                        >
                            <template #body="{ data }">
                                <Icon icon="AvatarFilled" medium />
                                {{ data.user.user_name }}
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
                        <Column header="Actions" sortable>
                            <template #body="{ data }">
                                <button
                                    class="btn btn-icon"
                                    @click="tryDelete(data)"
                                >
                                    <font-awesome-icon
                                        icon="fa-regular fa-trash-can"
                                    />
                                </button>
                            </template>
                        </Column>
                    </DataTable>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped type="scss">
.application-dropdown {
    width: 304px;
}

:deep(.p-inputtext) {
    border-bottom: none;
}

:deep(.p-datatable-thead .p-sortable-column) {
    /* Light Theme/Layer accent/$layer-accent-hover-01 */
    background: #d2d2d4;
    height: 32px;
    padding: 0 1rem;
    font-family: BC Sans;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.1599999964237213px;
    text-align: left;
    border: none;
}
:deep(.p-datatable .p-datatable-tbody > tr > td) {
    text-align: left;
    border: 1px solid #dee2e6;
    border-width: 1px 0 0 0;
    padding: 0 1rem;
    font-family: 'BC Sans';
    font-style: normal;
    font-weight: 400;
    font-size: 14px;
    line-height: 18px;
    letter-spacing: 0.16px;
}

.dashboard-button {
    padding: 16px;

    width: 235px;
    height: 48px;
    border-radius: 4px;

    /* Inside auto layout */

    /* Body styles/body-compact-01 */
    font-family: 'BC Sans';
    font-style: normal;
    font-weight: 400;
    font-size: 14px;
    line-height: 18px;
    /* identical to box height, or 129% */
    letter-spacing: 0.16px;

    text-align: left !important;
    /* Light Theme/Text/$text-on-color */
    color: #ffffff;

    vertical-align: middle;
}
.p-datatable-header {
    padding: 0px !important;
}

.access-table {
    margin-top: 79px;
    background: #ffffff;
    border-radius: 4px 4px 0px 0px;
    border: 2px solid #dfdfe1;
}
.table-header {
    padding: 16px 16px 24px;
}

.table-header h3 {
    /* Fixed heading styles/heading-03 */
    font-family: 'BC Sans';
    font-style: normal;
    font-weight: 400;
    font-size: 20px;
    line-height: 28px;
    /* identical to box height, or 140% */

    /* Light Theme/Text/$text-primary */
    color: #131315;

    /* Inside auto layout */
    flex: none;
    order: 0;
    align-self: stretch;
    flex-grow: 0;
}

.table-header span {
    /* Body styles/body-compact-01 */
    font-family: 'BC Sans';
    font-style: normal;
    font-weight: 400;
    font-size: 14px;
    line-height: 18px;
    /* identical to box height, or 129% */
    letter-spacing: 0.16px;

    /* Light Theme/Text/$text-secondary */
    color: #606062;

    /* Inside auto layout */
    flex: none;
    order: 1;
    align-self: stretch;
    flex-grow: 0;
}
</style>
