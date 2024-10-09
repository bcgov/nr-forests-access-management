<script setup lang="ts">
import { reactive, ref, computed, type PropType } from "vue";
import { FilterMatchMode } from "primevue/api";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { useConfirm } from "primevue/useconfirm";
import ConfirmDialog from "primevue/confirmdialog";
import ProgressSpinner from "primevue/progressspinner";

import { IconSize } from "@/enum/IconEnum";
import { routeItems } from "@/router/RouteItem";
import ConfirmDialogtext from "@/components/managePermissions/ConfirmDialogText.vue";
import DataTableHeader from "@/components/managePermissions/table/DataTableHeader.vue";
import NewUserTag from "@/components/common/NewUserTag.vue";
import {
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
    NEW_ACCESS_STYLE_IN_TABLE,
} from "@/store/Constants";
import { isNewAccess } from "@/services/utils";

import type { FamAppAdminGetResponse } from "fam-admin-mgmt-api/model";

type emit = (e: "deleteAppAdmin", item: FamAppAdminGetResponse) => void;
const confirm = useConfirm();
const emit = defineEmits<emit>();

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    applicationAdmins: {
        type: [Array] as PropType<FamAppAdminGetResponse[] | undefined>,
        required: true,
    },
    newIds: {
        type: String,
        default: "",
    },
});
const newAppAdminIds = computed(() => {
    return props.newIds.split(",");
});

const adminFilters = ref({
    global: { value: "", matchMode: FilterMatchMode.CONTAINS },
});

const adminSearchChange = (newvalue: string) => {
    adminFilters.value.global.value = newvalue;
};

const confirmDeleteData = reactive({
    adminName: "",
    role: "ADMIN",
});

const deleteAdmin = (admin: FamAppAdminGetResponse) => {
    confirmDeleteData.adminName = admin.user.user_name;
    confirm.require({
        group: "deleteAdmin",
        header: "Remove Access",
        rejectLabel: "Cancel",
        acceptLabel: "Remove",
        accept: () => {
            emit("deleteAppAdmin", admin);
        },
    });
};

const highlightNewAppAdminAccesRow = (rowData: any) => {
    if (isNewAccess(newAppAdminIds.value, rowData.application_admin_id)) {
        return NEW_ACCESS_STYLE_IN_TABLE;
    }
};
</script>

<template>
    <ConfirmDialog group="deleteAdmin">
        <template #message>
            <ConfirmDialogtext
                :userName="confirmDeleteData.adminName"
                :role="confirmDeleteData.role"
            />
        </template>
    </ConfirmDialog>
    <div class="data-table-container">
        <div class="custom-data-table">
            <DataTableHeader
                btnLabel="Add application admin"
                :btnRoute="routeItems.grantAppAdmin.path"
                :filter="adminFilters['global'].value"
                @change="adminSearchChange"
            />
            <DataTable
                v-model:filters="adminFilters"
                :value="props.applicationAdmins"
                paginator
                :rows="50"
                :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
                filterDisplay="menu"
                :loading="props.loading"
                :globalFilterFields="[
                    'user.user_name',
                    'application.application_name',
                    'user.user_type.description',
                    'user.first_name',
                    'user.last_name',
                    'user.email',
                    'role.role_name',
                    'application.app_environment',
                ]"
                :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
                stripedRows
                :rowStyle="highlightNewAppAdminAccesRow"
            >
                <template #empty> No user found. </template>
                <template #loading>
                    <ProgressSpinner aria-label="Loading" />
                </template>
                <Column header="User Name" sortable field="user.user_name">
                    <template #body="{ data }">
                        <NewUserTag
                            v-if="
                                isNewAccess(
                                    newAppAdminIds,
                                    data.application_admin_id
                                )
                            "
                        />
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
                <Column field="user.first_name" header="Full Name" sortable>
                    <template #body="{ data }">
                        {{
                            data.user.first_name && data.user.last_name
                                ? data.user.first_name +
                                  " " +
                                  data.user.last_name
                                : ""
                        }}
                    </template>
                </Column>
                <Column field="user.email" header="Email" sortable></Column>
                <Column
                    field="application.application_name"
                    header="Application"
                    sortable
                ></Column>
                <Column
                    field="application.app_environment"
                    header="Environment"
                    sortable
                ></Column>
                <Column field="role.role_name" header="Role" sortable>
                    <template #body="{ data }"> Admin </template></Column
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
                            title="Delete application admin"
                            class="btn btn-icon"
                            @click="deleteAdmin(data)"
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
@import "@/assets/styles/base.scss";
</style>
