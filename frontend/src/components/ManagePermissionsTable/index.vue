<script setup lang="ts">
import RecentlyViewedIcon from "@carbon/icons-vue/es/recently-viewed/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import { useMutation, useQuery } from "@tanstack/vue-query";
import { isAxiosError } from "axios";
import {
    type FamAccessControlPrivilegeGetResponse,
    type FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
import type { FamApplicationUserRoleAssignmentGetSchema } from "fam-app-acsctl-api/model";
import { FilterMatchMode } from "primevue/api";
import Column from "primevue/column";
import ConfirmDialog from "primevue/confirmdialog";
import DataTable from "primevue/datatable";
import { useConfirm } from "primevue/useconfirm";
import { nextTick, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import TableSkeleton from "@/components/Skeletons/TableSkeleton.vue";
import TableHeaderTitle from "@/components/Table/TableHeaderTitle.vue";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import Chip from "@/components/UI/Chip.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import {
    DEFAULT_ROW_PER_PAGE,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from "@/constants/constants";
import {
    AddAppPermissionRoute,
    AddFamPermissionRoute,
    UserDetailsRoute,
} from "@/router/routes";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { selectedApp } from "@/store/ApplicationState";
import { ManagePermissionsTableEnum } from "@/types/ManagePermissionsTypes";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import { formatAxiosError } from "@/utils/ApiUtils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import {
    NewAppAdminQueryParamKey,
    NewDelegatedAddminQueryParamKey,
} from "@/views/AddAppPermission/utils";
import { NewFamAdminQueryParamKey } from "@/views/AddFamPermission/utils";

import ConfirmDialogText from "./ConfirmDialogText.vue";
import NewUserTag from "./NewUserTag.vue";
import {
    createNotification,
    deleteAppUserRoleNotificationContext,
    deleteDelegatedAdminNotificationContext,
    deleteFamPermissionNotificationContext,
    filterList,
    getGrantButtonLabel,
    getHeaders,
    getTableHeaderDescription,
    getTableHeaderTitle,
    NEW_ACCESS_STYLE_IN_TABLE,
    type ConfirmTextType,
} from "./utils";

const router = useRouter();
const route = useRoute();

const environment = new EnvironmentSettings();

const newFamAdminIds = route.query[NewFamAdminQueryParamKey]
    ? String(route.query[NewFamAdminQueryParamKey]).split(",").map(Number)
    : [];

const newAppUserIds = route.query[NewAppAdminQueryParamKey]
    ? String(route.query[NewAppAdminQueryParamKey]).split(",").map(Number)
    : [];

const newDelegatedAdminIds = route.query[NewDelegatedAddminQueryParamKey]
    ? String(route.query[NewDelegatedAddminQueryParamKey])
          .split(",")
          .map(Number)
    : [];

const props = defineProps<{
    tableType: ManagePermissionsTableEnum;
    appName: string;
    appId: number;
    addNotifications: (newNotifications: PermissionNotificationType[]) => void;
}>();

// Fam App Admins data query
const appAdminQuery = useQuery({
    queryKey: ["application_admins"],
    queryFn: () =>
        AdminMgmtApiService.applicationAdminApi
            .getApplicationAdmins()
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: props.tableType === ManagePermissionsTableEnum.AppAdmin,
    select: (data) => {
        // Move matching IDs to the start of the array
        const sortedByUserName = data.sort((a, b) =>
            a.user.user_name.localeCompare(b.user.user_name)
        );
        return [
            ...sortedByUserName.filter((item) =>
                newFamAdminIds.includes(item.application_admin_id)
            ),
            ...sortedByUserName.filter(
                (item) => !newFamAdminIds.includes(item.application_admin_id)
            ),
        ];
    },
});

// App users data query
const appUserQuery = useQuery({
    queryKey: ["fam_applications", props.appId, "user_role_assignment"],
    queryFn: () =>
        AppActlApiService.applicationsApi
            .getFamApplicationUserRoleAssignment(props.appId)
            .then((res) => res.data.results),
    refetchOnMount: "always",
    enabled: props.tableType === ManagePermissionsTableEnum.AppUser,
    select: (data) => {
        const sortedByUserName = data.sort((a, b) =>
            a.user.user_name.localeCompare(b.user.user_name)
        );
        // Move matching IDs to the start of the array
        return [
            ...sortedByUserName.filter((item) =>
                newAppUserIds.includes(item.user_role_xref_id)
            ),
            ...sortedByUserName.filter(
                (item) => !newAppUserIds.includes(item.user_role_xref_id)
            ),
        ];
    },
});

// Delegated admin data query
const delegatedAdminQuery = useQuery({
    queryKey: ["access_control_privileges", { application_id: props.appId }],
    queryFn: () =>
        AdminMgmtApiService.delegatedAdminApi
            .getAccessControlPrivilegesByApplicationId(props.appId)
            .then((res) => res.data.results),
    refetchOnMount: "always",
    enabled: props.tableType === ManagePermissionsTableEnum.DelegatedAdmin,
    select: (data) => {
        const sortedByUserName = data.sort((a, b) =>
            a.user.user_name.localeCompare(b.user.user_name)
        );
        // Move matching IDs to the start of the array
        return [
            ...sortedByUserName.filter((item) =>
                newDelegatedAdminIds.includes(item.access_control_privilege_id)
            ),
            ...sortedByUserName.filter(
                (item) =>
                    !newDelegatedAdminIds.includes(
                        item.access_control_privilege_id
                    )
            ),
        ];
    },
});

const tableFilter = ref({
    global: { value: "", matchMode: FilterMatchMode.CONTAINS },
});

const handleSearchChange = (newValue: string) => {
    tableFilter.value.global.value = newValue;
};

const getTableRows = () => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.data.value ?? [];
        case ManagePermissionsTableEnum.AppUser:
            return appUserQuery.data.value ?? [];
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return delegatedAdminQuery.data.value ?? [];
        default:
            return [];
    }
};

// Get the query loading status
const isQueryLoading = (): boolean => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.isLoading.value;
        case ManagePermissionsTableEnum.AppUser:
            return appUserQuery.isLoading.value;
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return delegatedAdminQuery.isLoading.value;
        default:
            return false;
    }
};

// Get the query fetching status
const isQueryError = (): boolean => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.isError.value;
        case ManagePermissionsTableEnum.AppUser:
            return appUserQuery.isError.value;
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return delegatedAdminQuery.isError.value;
        default:
            return false;
    }
};

const getQueryErrorValue = () => {
    let error = null;
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            error = appAdminQuery.error.value;
            break;
        case ManagePermissionsTableEnum.AppUser:
            error = appUserQuery.error.value;
            break;
        case ManagePermissionsTableEnum.DelegatedAdmin:
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
    if (props.tableType === ManagePermissionsTableEnum.AppAdmin) {
        router.push({ name: AddFamPermissionRoute.name });
    } else if (props.tableType === ManagePermissionsTableEnum.AppUser) {
        router.push({
            name: AddAppPermissionRoute.name,
            query: {
                requestType: "addUserPermission",
                applicationId: props.appId,
            },
        });
    } else if (props.tableType === ManagePermissionsTableEnum.DelegatedAdmin) {
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

const deleteAppUserRoleMutation = useMutation({
    mutationFn: (appUser: FamApplicationUserRoleAssignmentGetSchema) =>
        AppActlApiService.userRoleAssignmentApi.deleteUserRoleAssignment(
            appUser.user_role_xref_id
        ),
    onSuccess: (_data, variables) => {
        props.addNotifications([
            createNotification(
                true,
                variables,
                null,
                deleteAppUserRoleNotificationContext
            ),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(
                false,
                variables,
                error,
                deleteAppUserRoleNotificationContext
            ),
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
                deleteDelegatedAdminNotificationContext
            ),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(
                false,
                variables,
                error,
                deleteDelegatedAdminNotificationContext
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
                deleteFamPermissionNotificationContext
            ),
        ]);
    },
    onError: (error, variables) => {
        props.addNotifications([
            createNotification(
                false,
                variables,
                error,
                deleteFamPermissionNotificationContext
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

    if (props.tableType === ManagePermissionsTableEnum.AppUser) {
        const appUser =
            privilegeObject as FamApplicationUserRoleAssignmentGetSchema;
        setConfirmTextProps(
            userName,
            appUser.role.display_name ?? "",
            props.appName
        );
        showConfirmDialog("Remove Access", () =>
            deleteAppUserRoleMutation.mutate(appUser)
        );
    }

    if (props.tableType === ManagePermissionsTableEnum.DelegatedAdmin) {
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

    if (props.tableType === ManagePermissionsTableEnum.AppAdmin) {
        const famAdmin = privilegeObject as FamAppAdminGetResponse;
        setConfirmTextProps(userName, "Admin", props.appName);
        showConfirmDialog("Remove Access", () =>
            deleteFamPermissionMutation.mutate(famAdmin)
        );
    }
};

// New tag logic
const highlightNewUserAccessRow = (
    rowData:
        | FamApplicationUserRoleAssignmentGetSchema
        | FamAccessControlPrivilegeGetResponse
        | FamAppAdminGetResponse
): object | undefined => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            const famAdin = rowData as FamAppAdminGetResponse;
            if (newFamAdminIds.includes(famAdin.application_admin_id)) {
                return NEW_ACCESS_STYLE_IN_TABLE;
            }
            return undefined;
        case ManagePermissionsTableEnum.AppUser:
            const appAdmin =
                rowData as FamApplicationUserRoleAssignmentGetSchema;
            if (newAppUserIds.includes(appAdmin.user_role_xref_id)) {
                return NEW_ACCESS_STYLE_IN_TABLE;
            }
            return undefined;
        case ManagePermissionsTableEnum.DelegatedAdmin:
            const delegatedAdmin =
                rowData as FamAccessControlPrivilegeGetResponse;
            if (
                newDelegatedAdminIds.includes(
                    delegatedAdmin.access_control_privilege_id
                )
            ) {
                return NEW_ACCESS_STYLE_IN_TABLE;
            }
            return undefined;
        default:
            return undefined;
    }
};

/**
 * DataTable 'Organization' column display expression.
 * @param {FamApplicationUserRoleAssignmentGetSchema | FamAccessControlPrivilegeGetResponse} data - provided
 *        datatable data to extract and format forest client information for the 'Organization' column. Only
 *        user table and delegated admin table have this column.
 */
const displayForestClient = (
    data:
        | FamApplicationUserRoleAssignmentGetSchema
        | FamAccessControlPrivilegeGetResponse
) => {
    if (props.tableType === ManagePermissionsTableEnum.AppUser) {
        const userData = data as FamApplicationUserRoleAssignmentGetSchema;
        const forestClientData = userData.role.forest_client;
        // Display formatted forest client display name.
        return forestClientData
            ? formatForestClientDisplayName(
                  forestClientData.forest_client_number,
                  forestClientData.client_name
              )
            : "";
    } else {
        // For delegated admin data.
        // TODO: No client name available for search from backend yet, implement soon. Only display client number. # noqa NOSONAR
        const delegatedAdminData = data as FamAccessControlPrivilegeGetResponse;
        const forestClientData = delegatedAdminData.role.client_number;
        return forestClientData?.forest_client_number;
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
            :title="getTableHeaderTitle(appName, tableType)"
            :description="getTableHeaderDescription(appName, tableType)"
        />

        <TableToolbar
            :filter="tableFilter['global'].value"
            :btn-label="getGrantButtonLabel(tableType)"
            :btn-on-click="handleAddButton"
            input-placeholder="Search by keyword"
            @change="handleSearchChange"
        />

        <TableSkeleton
            v-if="isQueryLoading()"
            :headers="getHeaders(tableType)"
            :row-amount="5"
        />
        <ErrorText
            v-else-if="isQueryError()"
            :error-msg="getQueryErrorValue()"
        />
        <DataTable
            v-else
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
            :rowStyle="highlightNewUserAccessRow"
        >
            <template #empty> No user found. </template>

            <Column header="User Name" field="user.user_name" sortable>
                <template #body="{ data }">
                    <NewUserTag v-if="highlightNewUserAccessRow(data)" />
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
                v-if="tableType === ManagePermissionsTableEnum.AppAdmin"
                header="Application"
                field="application.application_description"
                sortable
            />

            <Column
                v-if="tableType === ManagePermissionsTableEnum.AppAdmin"
                header="Environment"
                field="application.app_environment"
                sortable
            />

            <Column
                v-if="tableType !== ManagePermissionsTableEnum.AppAdmin"
                :field="
                    tableType === ManagePermissionsTableEnum.AppUser
                        ? 'role.forest_client.forest_client_number'
                        : 'role.client_number.forest_client_number'
                "
                :sort-field="
                    tableType === ManagePermissionsTableEnum.AppUser
                        ? 'role.forest_client.forest_client_number'
                        : 'role.client_number.forest_client_number'
                "
                header="Organization"
                sortable
            >
                <template #body="{ data }">
                    {{ displayForestClient(data) }}
                </template>
            </Column>

            <Column
                :header="
                    tableType === ManagePermissionsTableEnum.DelegatedAdmin
                        ? 'Role Enabled To Assign'
                        : 'Role'
                "
                field="roleDisplay"
                :sortable="tableType !== ManagePermissionsTableEnum.AppAdmin"
                sort-field="role.display_name"
            >
                <template #body="{ data }">
                    <Chip
                        :label="
                            tableType === ManagePermissionsTableEnum.AppAdmin
                                ? 'Admin'
                                : data.role.display_name
                        "
                    />
                </template>
            </Column>

            <Column header="Action">
                <template #body="{ data }">
                    <button
                        v-if="tableType !== ManagePermissionsTableEnum.AppAdmin"
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
