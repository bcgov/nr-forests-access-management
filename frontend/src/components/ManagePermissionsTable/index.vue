<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
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
import TableSkeleton from "@/components/Skeletons/TableSkeleton.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import Chip from "@/components/UI/Chip.vue";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
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
import { NewFamAdminQueryParamKey } from "@/views/AddFamPermission/utils";
import {
    NewAppAdminQueryParamKey,
    NewDelegatedAddminQueryParamKey,
} from "@/views/AddAppPermission/utils";

import NewUserTag from "./NewUserTag.vue";
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
    NEW_ACCESS_STYLE_IN_TABLE,
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
    authGroup: AdminRoleAuthGroup;
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
    enabled: props.authGroup === "FAM_ADMIN",
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
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: props.authGroup === "APP_ADMIN",
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
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled:
        props.authGroup === "DELEGATED_ADMIN" &&
        // DelegatedAdminFeatureFlag
        !environment.isProdEnvironment(),
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
            return appAdminQuery.isLoading.value;
        case "APP_ADMIN":
            return appUserQuery.isLoading.value;
        case "DELEGATED_ADMIN":
            return delegatedAdminQuery.isLoading.value;
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

// New tag logic
const highlightNewUserAccessRow = (
    rowData:
        | FamApplicationUserRoleAssignmentGetSchema
        | FamAccessControlPrivilegeGetResponse
        | FamAppAdminGetResponse
): object | undefined => {
    switch (props.authGroup) {
        case "FAM_ADMIN":
            const famAdin = rowData as FamAppAdminGetResponse;
            if (newFamAdminIds.includes(famAdin.application_admin_id)) {
                return NEW_ACCESS_STYLE_IN_TABLE;
            }
            return undefined;
        case "APP_ADMIN":
            const appAdmin =
                rowData as FamApplicationUserRoleAssignmentGetSchema;
            if (newAppUserIds.includes(appAdmin.user_role_xref_id)) {
                return NEW_ACCESS_STYLE_IN_TABLE;
            }
            return undefined;
        case "DELEGATED_ADMIN":
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
