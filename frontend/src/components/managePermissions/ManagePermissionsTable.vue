<script setup lang="ts">
// Package imports
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { FilterMatchMode } from "primevue/api";
import ConfirmDialog from "primevue/confirmdialog";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { useMutation, useQuery } from "@tanstack/vue-query";
import RecentlyViewedIcon from "@carbon/icons-vue/es/recently-viewed/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import { isAxiosError } from "axios";
import { useConfirm } from "primevue/useconfirm";
import type {
    AdminRoleAuthGroup,
    FamAccessControlPrivilegeGetResponse,
    FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
import type { FamApplicationUserRoleAssignmentGetSchema } from "fam-app-acsctl-api/model";

import TableToolbar from "@/components/Table/TableToolbar.vue";
import TableHeaderTitle from "@/components/Table/TableHeaderTitle.vue";
import TableSkeleton from "@/components/Table/TableSkeleton.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import Chip from "@/components/UI/Chip.vue";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { formatUserNameAndId } from "@/utils/UserUtils";
import {
    DEFAULT_ROW_PER_PAGE,
    TABLE_ROWS_PER_PAGE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
} from "@/store/Constants";
import { formatAxiosError } from "@/utils/ApiUtils";
import {
    AddAppPermissionRoute,
    AddFamPermissionRoute,
    UserDetailsRoute,
} from "@/router/routes";
import { selectedApp } from "@/store/ApplicationState";
import type { PermissionNotificationType } from "@/types/ManagePermissionsTypes";

import ConfirmDialogText from "./ConfirmDialogText.vue";
import {
    getTableHeaderDescription,
    getTableHeaderTitle,
    getGrantButtonLabel,
    filterList,
    getHeaders,
    type ConfirmTextType,
    createNotification,
    deleteAppAdminContext,
    deleteDelegatedAdminContext,
    deleteFamPermissionContext,
} from "./utils";

const router = useRouter();

const props = defineProps<{
    authGroup: AdminRoleAuthGroup;
    appName: string;
    appId: number;
    addNotifications: (newNotifications: PermissionNotificationType[]) => void;
}>();

const appAdminQuery = useQuery({
    queryKey: ["application_admins"],
    queryFn: () =>
        AdminMgmtApiService.applicationAdminApi
            .getApplicationAdmins()
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: props.authGroup === "FAM_ADMIN",
});
console.log(props.authGroup);
const appUserQuery = useQuery({
    queryKey: ["fam_applications", props.appId, "user_role_assignment"],
    queryFn: () =>
        AppActlApiService.applicationsApi
            .getFamApplicationUserRoleAssignment(props.appId)
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: props.authGroup === "APP_ADMIN",
});

const delegatedAdminQuery = useQuery({
    queryKey: ["access_control_privileges", { application_id: props.appId }],
    queryFn: () =>
        AdminMgmtApiService.delegatedAdminApi
            .getAccessControlPrivilegesByApplicationId(props.appId)
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: props.authGroup === "DELEGATED_ADMIN",
});

const tableFilter = ref({
    global: { value: "", matchMode: FilterMatchMode.CONTAINS },
});

const handleSearchChange = (newValue: string) => {
    tableFilter.value.global.value = newValue;
};

const getTableRows = () => {
    switch (props.authGroup) {
        case "FAM_ADMIN":
            return appAdminQuery.data.value ?? [];
        case "APP_ADMIN":
            return appUserQuery.data.value ?? [];
        case "DELEGATED_ADMIN":
            return delegatedAdminQuery.data.value ?? [];
        default:
            return [];
    }
};

// Get the query loading status
const isQueryLoading = (): boolean => {
    switch (props.authGroup) {
        case "FAM_ADMIN":
            return appAdminQuery.isFetching.value;
        case "APP_ADMIN":
            return appUserQuery.isFetching.value;
        case "DELEGATED_ADMIN":
            return delegatedAdminQuery.isFetching.value;
        default:
            return false;
    }
};

// Get the query fetching status
const isQueryError = (): boolean => {
    switch (props.authGroup) {
        case "FAM_ADMIN":
            return appAdminQuery.isError.value;
        case "APP_ADMIN":
            return appUserQuery.isError.value;
        case "DELEGATED_ADMIN":
            return delegatedAdminQuery.isError.value;
        default:
            return false;
    }
};

const getQueryErrorValue = () => {
    let error = null;
    switch (props.authGroup) {
        case "FAM_ADMIN":
            error = appAdminQuery.error.value;
            break;
        case "APP_ADMIN":
            error = appUserQuery.error.value;
            break;
        case "DELEGATED_ADMIN":
            error = delegatedAdminQuery.error.value;
            break;
    }
    if (error) {
        return isAxiosError(error)
            ? `Failed to fetch data. ${formatAxiosError(error)}`
            : "Failed to fetch data.";
    }

    return undefined;
};

const handleAddButton = () => {
    if (props.authGroup === "FAM_ADMIN") {
        router.push({ name: AddFamPermissionRoute.name });
    } else if (props.authGroup === "APP_ADMIN") {
        router.push({
            name: AddAppPermissionRoute.name,
            query: {
                requestType: "addUserPermission",
                applicationId: props.appId,
            },
        });
    } else if (props.authGroup === "DELEGATED_ADMIN") {
        router.push({
            name: AddAppPermissionRoute.name,
            query: {
                requestType: "addDelegatedAdmin",
                applicationId: props.appId,
            },
        });
    }
};

const navigateToUserDetails = (userId: string) => {
    router.push({
        name: UserDetailsRoute.name,
        params: {
            applicationId: selectedApp.value?.id,
            userId,
        },
    });
};

const confirm = useConfirm();

const confirmTextProps = ref<ConfirmTextType>();

const deleteAppAdminMutation = useMutation({
    mutationFn: (admin: FamApplicationUserRoleAssignmentGetSchema) =>
        AppActlApiService.userRoleAssignmentApi.deleteUserRoleAssignment(
            admin.user_role_xref_id
        ),
    onSuccess: (_data, variables) => {
        props.addNotifications([
            createNotification(true, variables, null, deleteAppAdminContext),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(false, variables, error, deleteAppAdminContext),
        ]);
    },
    onSettled: () => appUserQuery.refetch(),
});

const deleteDelegatedAdminMutation = useMutation({
    mutationFn: (admin: FamAccessControlPrivilegeGetResponse) =>
        AdminMgmtApiService.delegatedAdminApi.deleteAccessControlPrivilege(
            admin.access_control_privilege_id
        ),
    onSuccess: (_data, variables) => {
        props.addNotifications([
            createNotification(
                true,
                variables,
                null,
                deleteDelegatedAdminContext
            ),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(
                false,
                variables,
                error,
                deleteDelegatedAdminContext
            ),
        ]);
    },
    onSettled: () => delegatedAdminQuery.refetch(),
});

const deleteFamPermissionMutation = useMutation({
    mutationFn: (admin: FamAppAdminGetResponse) =>
        AdminMgmtApiService.applicationAdminApi.deleteApplicationAdmin(
            admin.application_admin_id
        ),
    onSuccess: (_data, variables) => {
        props.addNotifications([
            createNotification(
                true,
                variables,
                null,
                deleteFamPermissionContext
            ),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(
                false,
                variables,
                error,
                deleteFamPermissionContext
            ),
        ]);
    },
    onSettled: () => appAdminQuery.refetch(),
});

const setConfirmTextProps = (
    userName: string,
    role: string,
    appName: string
) => {
    confirmTextProps.value = {
        userName,
        role,
        appName,
        customMsg: undefined,
    };
};

const showConfirmDialog = (header: string, onAccept: () => void) => {
    // Next tick is used to prevent the dialog showing twice, not sure why
    nextTick(() =>
        confirm.require({
            group: "deleteAppPermission",
            header,
            rejectLabel: "Cancel",
            acceptLabel: "Remove",
            accept: () => {
                onAccept();
                confirmTextProps.value = undefined;
            },
            reject: () => {
                confirmTextProps.value = undefined;
            },
        })
    );
};

const handleDelete = (
    privilegeObject:
        | FamApplicationUserRoleAssignmentGetSchema
        | FamAccessControlPrivilegeGetResponse
        | FamAppAdminGetResponse
) => {
    const userName = formatUserNameAndId(
        privilegeObject.user.user_name,
        privilegeObject.user.first_name,
        privilegeObject.user.last_name
    );

    if (props.authGroup === "APP_ADMIN") {
        const admin =
            privilegeObject as FamApplicationUserRoleAssignmentGetSchema;
        setConfirmTextProps(
            userName,
            admin.role.display_name ?? "",
            props.appName
        );
        showConfirmDialog("Remove Access", () =>
            deleteAppAdminMutation.mutate(admin)
        );
    }

    if (props.authGroup === "DELEGATED_ADMIN") {
        const delegatedAdmin =
            privilegeObject as FamAccessControlPrivilegeGetResponse;
        setConfirmTextProps(
            userName,
            delegatedAdmin.role.display_name ?? "",
            props.appName
        );
        showConfirmDialog("Remove Privilege", () =>
            deleteDelegatedAdminMutation.mutate(delegatedAdmin)
        );
    }

    if (props.authGroup === "FAM_ADMIN") {
        const famAdmin = privilegeObject as FamAppAdminGetResponse;
        setConfirmTextProps(userName, "Admin", props.appName);
        showConfirmDialog("Remove Access", () =>
            deleteFamPermissionMutation.mutate(famAdmin)
        );
    }
};
</script>

<template>
    <div class="fam-table">
        <ConfirmDialog group="deleteAppPermission" v-if="confirmTextProps">
            <template #message>
                <ConfirmDialogText
                    :user-name="confirmTextProps.userName"
                    :role="confirmTextProps.role"
                    :app-name="confirmTextProps.appName"
                    :custom-msg="confirmTextProps.customMsg"
                />
            </template>
        </ConfirmDialog>
        <TableHeaderTitle
            :title="getTableHeaderTitle(appName, authGroup)"
            :description="getTableHeaderDescription(appName, authGroup)"
        />

        <TableToolbar
            :filter="tableFilter['global'].value"
            :btn-label="getGrantButtonLabel(authGroup)"
            :btn-on-click="handleAddButton"
            input-placeholder="Search by keyword"
            @change="handleSearchChange"
        />

        <TableSkeleton
            v-if="isQueryLoading()"
            :headers="getHeaders(authGroup)"
            :row-amount="5"
        />
        <ErrorText v-if="isQueryError()" :error-msg="getQueryErrorValue()" />
        <DataTable
            v-if="!isQueryLoading() && !isQueryError()"
            :value="getTableRows()"
            :total-records="getTableRows().length"
            removableSort
            stripedRows
            v-model:filters="tableFilter"
            filterDisplay="menu"
            :globalFilterFields="filterList"
            paginator
            :rows="DEFAULT_ROW_PER_PAGE"
            :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
            :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
            :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
        >
            <template #empty> No user found. </template>

            <Column header="User Name" field="user.user_name" sortable>
                <template #body="{ data }">
                    <!-- <NewUserTag
                        v-if="
                            isNewAccess(
                                newUserAccessIds,
                                data.user_role_xref_id
                            )
                        "
                    /> -->
                    <span>{{ data.user.user_name }}</span>
                </template>
            </Column>

            <Column
                header="Domain"
                field="user.user_type.description"
                sortable
            />

            <Column
                header="Full Name"
                sortable
                field="fullName"
                sort-field="user.first_name"
            >
                <template #body="{ data }">
                    {{
                        formatUserNameAndId(
                            null,
                            data.user.first_name,
                            data.user.last_name
                        )
                    }}
                </template>
            </Column>

            <Column header="Email" field="user.email" sortable />

            <Column
                v-if="authGroup === 'FAM_ADMIN'"
                header="Application"
                field="application.application_description"
                sortable
            />

            <Column
                v-if="authGroup === 'FAM_ADMIN'"
                header="Environment"
                field="application.app_environment"
                sortable
            />

            <Column
                v-if="authGroup !== 'FAM_ADMIN'"
                :field="
                    authGroup === 'APP_ADMIN'
                        ? 'role.forest_client.forest_client_number'
                        : 'role.client_number.forest_client_number'
                "
                header="Client Number"
                sortable
            ></Column>

            <Column
                :header="
                    authGroup === 'DELEGATED_ADMIN'
                        ? 'Role Enabled To Assign'
                        : 'Role'
                "
                field="roleDisplay"
                :sortable="authGroup !== 'FAM_ADMIN'"
                sort-field="role.display_name"
            >
                <template #body="{ data }">
                    <Chip
                        :label="
                            authGroup === 'FAM_ADMIN'
                                ? 'Admin'
                                : data.role.display_name
                        "
                    />
                </template>
            </Column>

            <Column header="Action">
                <template #body="{ data }">
                    <button
                        v-if="authGroup !== 'FAM_ADMIN'"
                        title="User permission history"
                        class="btn btn-icon"
                        @click="navigateToUserDetails(data.user_id)"
                    >
                        <RecentlyViewedIcon />
                    </button>

                    <button
                        title="Delete user"
                        class="btn btn-icon"
                        @click="handleDelete(data)"
                    >
                        <TrashIcon />
                    </button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
<style lang="scss">
.fam-table {
    .error-text-container {
        height: 2rem;
        padding: 1rem;
    }
}
</style>
