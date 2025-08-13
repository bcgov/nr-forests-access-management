<script setup lang="ts">
import RecentlyViewedIcon from "@carbon/icons-vue/es/recently-viewed/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import { useMutation, useQuery } from "@tanstack/vue-query";
import { isAxiosError } from "axios";
import {
    type FamAccessControlPrivilegeGetResponse,
    type FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
import {
    SortOrderEnum,
    type FamApplicationUserRoleAssignmentGetSchema,
} from "fam-app-acsctl-api/model";
import { FilterMatchMode } from "primevue/api";
import Column from "primevue/column";
import ConfirmDialog from "primevue/confirmdialog";
import DataTable, {
    type DataTablePageEvent,
    type DataTableSortEvent,
} from "primevue/datatable";
import { useConfirm } from "primevue/useconfirm";
import { computed, nextTick, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
    downloadCsvFromResponse,
    exportDataTableApiCall,
    getOrganizationName,
    sortFieldToEnum,
} from "@/components/ManagePermissionsTable/utils";
import TableSkeleton from "@/components/Skeletons/TableSkeleton.vue";
import TableHeaderTitle from "@/components/Table/TableHeaderTitle.vue";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import Chip from "@/components/UI/Chip.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import Spinner from "@/components/UI/Spinner.vue";
import {
    DEFAULT_ROW_PER_PAGE,
    MINIMUM_SEARCH_STR_LEN,
    TABLE_CURRENT_PAGE_REPORT_TEMPLATE,
    TABLE_PAGINATOR_TEMPLATE,
    TABLE_ROWS_PER_PAGE,
} from "@/constants/constants";
import { UserDetailsRoute } from "@/router/routes";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { selectedApp } from "@/store/ApplicationState";
import { ManagePermissionsTableEnum } from "@/types/ManagePermissionsTypes";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import type { PaginationType } from "@/types/PaginationTypes";
import { formatAxiosError } from "@/utils/ApiUtils";
import { utcToLocalDate } from "@/utils/DateUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { scrollToRef } from "@/utils/WindowUtils";
import {
    NewAppAdminQueryParamKey,
    NewDelegatedAddminQueryParamKey,
} from "@/views/AddAppPermission/utils";
import { NewFamAdminQueryParamKey } from "@/views/AddFamPermission/utils";
import DownloadIcon from "@carbon/icons-vue/es/download/16";
import ConfirmDialogText from "./ConfirmDialogText.vue";
import NewUserTag from "./NewUserTag.vue";
import {
    createNotification,
    defaultBackendPagination,
    deleteAppUserRoleNotificationContext,
    deleteDelegatedAdminNotificationContext,
    deleteFamPermissionNotificationContext,
    filterList,
    getHeaders,
    getTableHeaderDescription,
    getTableHeaderTitle,
    NEW_ACCESS_STYLE_IN_TABLE,
    type ConfirmTextType,
} from "./utils";

type TableRowType =
    | FamApplicationUserRoleAssignmentGetSchema
    | FamAccessControlPrivilegeGetResponse
    | FamAppAdminGetResponse;

const router = useRouter();
const route = useRoute();

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

const isAppAdminTable = props.tableType === ManagePermissionsTableEnum.AppAdmin;
const isAppUserTable = props.tableType === ManagePermissionsTableEnum.AppUser;
const isApplicationAdminTable =
    props.tableType === ManagePermissionsTableEnum.ApplicationAdmin;
const isDelegatedTable =
    props.tableType === ManagePermissionsTableEnum.DelegatedAdmin;

// Fam App Admins data query, this query has no pagination and create date
const appAdminQuery = useQuery({
    queryKey: ["application_admins"],
    queryFn: () =>
        AdminMgmtApiService.applicationAdminApi
            .getApplicationAdmins()
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: isAppAdminTable,
    select: (data) => {
        // Sort then move matching IDs to the start of the array
        const sortedByUserName = data.sort((a: any, b: any) =>
            a.user.user_name.localeCompare(b.user.user_name)
        );
        return [
            ...sortedByUserName.filter((item: any) =>
                newFamAdminIds.includes(item.application_admin_id)
            ),
            ...sortedByUserName.filter(
                (item: any) =>
                    !newFamAdminIds.includes(item.application_admin_id)
            ),
        ];
    },
});

const backendPagination = ref<PaginationType>(
    structuredClone(defaultBackendPagination)
);

/**
 * Indicates whether the backend pagination data is being fetched based on user input.
 *
 * This flag disables table interactions (such as sorting and pagination) while maintaining
 * the table's settings.
 * A skeleton loader is not used in this case, as the focus is on disabling interactions
 * instead of displaying loading placeholders.
 */
const isFetching = ref<boolean>(false);

// App users data query
const appUserQuery = useQuery({
    queryKey: [
        "fam-applications",
        props.appId,
        "user-role-assignment",
        {
            pageNumber: backendPagination.value.pageNumber,
            pageSize: backendPagination.value.pageSize,
            search: backendPagination.value.search,
            sortOrder: backendPagination.value.sortOrder,
            sortBy: backendPagination.value.sortBy,
        },
    ],
    queryFn: () =>
        AppActlApiService.applicationsApi
            .getFamApplicationUserRoleAssignment(
                props.appId,
                backendPagination.value.pageNumber,
                backendPagination.value.pageSize,
                backendPagination.value.search,
                backendPagination.value.sortOrder,
                backendPagination.value.sortBy
            )
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: isAppUserTable,
});

// Delegated admin data query
const delegatedAdminQuery = useQuery({
    queryKey: [
        "access-control-privileges",
        {
            application_id: props.appId,
            pageNumber: backendPagination.value.pageNumber,
            pageSize: backendPagination.value.pageSize,
            search: backendPagination.value.search,
            sortOrder: backendPagination.value.sortOrder,
            sortBy: backendPagination.value.sortBy,
        },
    ],
    queryFn: () =>
        AdminMgmtApiService.delegatedAdminApi
            .getAccessControlPrivilegesByApplicationId(
                props.appId,
                backendPagination.value.pageNumber,
                backendPagination.value.pageSize,
                backendPagination.value.search,
                backendPagination.value.sortOrder,
                backendPagination.value.sortBy
            )
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: isDelegatedTable,
});

// Application admins data query for specific application
const applicationAdminQuery = useQuery({
    queryKey: ["application_admins", "by_application", props.appId],
    queryFn: () =>
        AdminMgmtApiService.applicationAdminApi
            .getApplicationAdminsByApplicationId(props.appId)
            .then((res) => res.data),
    refetchOnMount: "always",
    enabled: isApplicationAdminTable,
    select: (data) => {
        // Sort by user name
        return data.sort((a: any, b: any) =>
            a.user.user_name.localeCompare(b.user.user_name)
        );
    },
});

const tableFilter = ref({
    global: { value: "", matchMode: FilterMatchMode.CONTAINS },
});

const handleSearchChange = (searchValue: string) => {
    tableFilter.value.global.value = searchValue;
};

const getTotalRecords = (): number => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.data.value?.length ?? 0;
        case ManagePermissionsTableEnum.AppUser:
            return appUserQuery.data.value?.meta.total ?? 0;
        case ManagePermissionsTableEnum.ApplicationAdmin:
            return applicationAdminQuery.data.value?.length ?? 0;
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return delegatedAdminQuery.data.value?.meta.total ?? 0;
        default:
            return 0;
    }
};

const hasUserRoleRecords = ref<boolean>(false);
const getTableRows = computed(() => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.data.value ?? [];
        case ManagePermissionsTableEnum.AppUser:
            const records = appUserQuery.data.value?.results ?? [];
            hasUserRoleRecords.value = records.length > 0 ? true : false;
            return records;
        case ManagePermissionsTableEnum.ApplicationAdmin:
            return applicationAdminQuery.data.value ?? [];
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return delegatedAdminQuery.data.value?.results ?? [];
        default:
            return [];
    }
});

// Get the query loading status
const isQueryLoading = (): boolean => {
    switch (props.tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return appAdminQuery.isLoading.value;
        case ManagePermissionsTableEnum.AppUser:
            return appUserQuery.isLoading.value;
        case ManagePermissionsTableEnum.ApplicationAdmin:
            return applicationAdminQuery.isLoading.value;
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
        case ManagePermissionsTableEnum.ApplicationAdmin:
            return applicationAdminQuery.isError.value;
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
        case ManagePermissionsTableEnum.ApplicationAdmin:
            error = applicationAdminQuery.error.value;
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

const navigateToUserDetails = (rowData: TableRowType) => {
    router.push({
        name: UserDetailsRoute.name,
        params: {
            appId: !isAppAdminTable
                ? selectedApp.value?.id
                : (rowData as FamAppAdminGetResponse).application_id,
            userId: rowData.user_id,
        },
    });
};

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

const confirm = useConfirm();

const confirmTextProps = ref<ConfirmTextType>();

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

const handleDelete = (privilegeObject: TableRowType) => {
    const userName = formatUserNameAndId(
        privilegeObject.user.user_name,
        privilegeObject.user.first_name,
        privilegeObject.user.last_name
    );

    if (isAppUserTable) {
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

    if (isDelegatedTable) {
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

    if (isAppAdminTable || isApplicationAdminTable) {
        const famAdmin = privilegeObject as FamAppAdminGetResponse;
        setConfirmTextProps(userName, "Admin", props.appName);
        showConfirmDialog("Remove Access", () =>
            deleteFamPermissionMutation.mutate(famAdmin)
        );
    }
};

// New tag logic
const highlightNewUserAccessRow = (
    rowData: TableRowType
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
        case ManagePermissionsTableEnum.ApplicationAdmin:
            // For application admins, we don't currently support highlighting new ones
            // as they are not added through the same workflow
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

/*
 * Below are lazy loading logic for backend paginated results
 */
const tableRef = ref<HTMLElement | null>(null);

const handlePageChange = (event: DataTablePageEvent): void => {
    if (isAppAdminTable || isApplicationAdminTable) {
        return;
    }

    isFetching.value = true;
    const pageNumToRequest = event.page + 1; // Convert to 1-based index
    const pageSizeToRequest = event.rows;
    backendPagination.value.pageNumber = pageNumToRequest;
    backendPagination.value.pageSize = pageSizeToRequest;

    if (isAppUserTable) {
        appUserQuery.refetch().finally(() => (isFetching.value = false));
    } else if (isDelegatedTable) {
        delegatedAdminQuery.refetch().finally(() => (isFetching.value = false));
    }
    scrollToRef(tableRef);
};

const handleSort = (event: DataTableSortEvent): void => {
    if (isAppAdminTable || isApplicationAdminTable) {
        return;
    }
    const { sortField, sortOrder } = event;
    isFetching.value = true;

    if (sortOrder === 0) {
        backendPagination.value.sortOrder = null;
        backendPagination.value.sortBy = null;
    } else {
        backendPagination.value.sortOrder =
            sortOrder === 1 ? SortOrderEnum.Asc : SortOrderEnum.Desc;
        backendPagination.value.sortBy = sortFieldToEnum(sortField);
    }

    if (isAppUserTable) {
        appUserQuery.refetch().finally(() => (isFetching.value = false));
    } else if (isDelegatedTable) {
        delegatedAdminQuery.refetch().finally(() => (isFetching.value = false));
    }
};

const showFilterError = ref<boolean>(false);

const firstRow = ref(0);

/**
 * Reset paginator to start from the first page
 */
const resetPageNumber = () => {
    firstRow.value = 0;
};

const handleFilter = (searchValue: string, isChanged: boolean) => {
    if (!isAppAdminTable && !isApplicationAdminTable && isChanged) {
        showFilterError.value = false;
        let strToSearch: string | null = searchValue;

        if (searchValue.length === 0) {
            strToSearch = null;
        } else if (searchValue.length < MINIMUM_SEARCH_STR_LEN) {
            showFilterError.value = true;
            return;
        }
        isFetching.value = true;
        backendPagination.value.search = strToSearch;
        backendPagination.value.pageNumber = 1;
        if (isAppUserTable) {
            appUserQuery.refetch().finally(() => {
                resetPageNumber();
                isFetching.value = false;
            });
        } else if (isDelegatedTable) {
            delegatedAdminQuery.refetch().finally(() => {
                resetPageNumber();
                isFetching.value = false;
            });
        }
    }
};

/**
 * Export CSV handling using TanStak.
 * Just a note:
 * TanStak only has function 'useMutation' that does not cache the data
 * although the api is a GET request but the name 'mutation' is quite strange
 * and normally 'mutation' is used for POST.
 */
const exportToCsvMutation = useMutation({
    mutationFn: () => exportDataTableApiCall(props.appId, props.tableType),
    onSuccess: (csvResponse) => {
        downloadCsvFromResponse(csvResponse);
    },
    onError: (error) => {
        throw new Error("Failed to download the CSV file.");
    },
});
const downloadManagePermissionsCSVData = () => {
    exportToCsvMutation.mutate();
};
</script>

<template>
    <div class="fam-table" ref="tableRef">
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
        <ErrorText
            v-if="showFilterError"
            :errorMsg="`Keyword must have at least ${MINIMUM_SEARCH_STR_LEN} characters`"
        />
        <div class="table-toolbar-container">
            <TableToolbar
                :filter="tableFilter['global'].value"
                input-placeholder="Search by keyword"
                @change="handleSearchChange"
                @blur="handleFilter"
            />
            <Button
                :disabled="getTotalRecords() === 0"
                @click="downloadManagePermissionsCSVData"
                :isLoading="exportToCsvMutation.isPending.value"
                outlined
                label="Download table as CSV file&nbsp;&nbsp;"
                :icon="DownloadIcon"
                aria-label="Download table as CSV file"
            />
        </div>

        <TableSkeleton
            v-if="isQueryLoading()"
            :headers="getHeaders(tableType)"
            :row-amount="5"
        />
        <ErrorText
            v-else-if="isQueryError()"
            :error-msg="getQueryErrorValue()"
        />
        <!-- Data Table -->
        <div v-else>
            <DataTable
                :lazy="!isAppAdminTable && !isApplicationAdminTable"
                :value="getTableRows"
                :total-records="getTotalRecords()"
                v-model:first="firstRow"
                removableSort
                stripedRows
                v-model:filters="tableFilter"
                filterDisplay="menu"
                :globalFilterFields="
                    isApplicationAdminTable ? undefined : filterList
                "
                :dataKey="
                    isApplicationAdminTable
                        ? 'application_admin_id'
                        : isAppUserTable
                        ? 'user_role_xref_id'
                        : isDelegatedTable
                        ? 'access_control_privilege_id'
                        : 'application_admin_id'
                "
                :paginator="!isApplicationAdminTable"
                :rows="DEFAULT_ROW_PER_PAGE"
                :rowsPerPageOptions="TABLE_ROWS_PER_PAGE"
                :paginatorTemplate="TABLE_PAGINATOR_TEMPLATE"
                :currentPageReportTemplate="TABLE_CURRENT_PAGE_REPORT_TEMPLATE"
                :rowStyle="highlightNewUserAccessRow"
                @page="handlePageChange"
                @sort="handleSort"
                :loading="isFetching"
            >
                <template #empty> No user found. </template>

                <template #loading><Spinner /></template>

                <Column header="User Name" field="user.user_name" sortable>
                    <template #body="{ data }">
                        <div class="nowrap-cell">
                            <NewUserTag
                                v-if="highlightNewUserAccessRow(data)"
                            />
                            <span>{{ data.user.user_name }}</span>
                        </div>
                    </template>
                </Column>

                <Column
                    header="Domain"
                    field="user.user_type.description"
                    sortable
                >
                    <template #body="{ data }">
                        <span>
                            {{ data.user.user_type.description }}
                        </span>
                    </template>
                </Column>

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
                    v-if="isAppAdminTable"
                    header="Application"
                    field="application.application_description"
                    sortable
                />

                <Column
                    v-if="isAppAdminTable"
                    header="Environment"
                    field="application.app_environment"
                    sortable
                />

                <Column
                    v-if="!isAppAdminTable && !isApplicationAdminTable"
                    field="role.forest_client.forest_client_number"
                    sort-field="role.forest_client.forest_client_number"
                    header="Organization"
                    sortable
                >
                    <template #body="{ data }">
                        {{ getOrganizationName(data) }}
                    </template>
                </Column>

                <Column
                    v-if="!isApplicationAdminTable"
                    :header="isAppUserTable ? 'Role' : 'Role Enabled To Assign'"
                    field="roleDisplay"
                    :sortable="!isAppAdminTable"
                    sort-field="role.display_name"
                >
                    <template #body="{ data }">
                        <Chip
                            :label="
                                isAppAdminTable
                                    ? 'Admin'
                                    : data.role.display_name
                            "
                        />
                    </template>
                </Column>

                <Column
                    v-if="!isAppAdminTable || isApplicationAdminTable"
                    header="Added On"
                    field="create_date"
                    sortable
                >
                    <template #body="{ data }">
                        <span>
                            {{ utcToLocalDate(data.create_date) }}
                        </span>
                    </template>
                </Column>

                <Column header="Action" class="action-col">
                    <template #body="{ data }">
                        <div class="nowrap-cell action-button-group">
                            <button
                                title="User permission history"
                                class="btn btn-icon"
                                @click="navigateToUserDetails(data)"
                            >
                                <RecentlyViewedIcon />
                            </button>

                            <button
                                v-if="!isApplicationAdminTable"
                                title="Delete user"
                                class="btn btn-icon"
                                @click="handleDelete(data)"
                            >
                                <TrashIcon />
                            </button>
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>
<style lang="scss">
.fam-table {
    border: 0 0.25rem 0.25rem 0.25rem;

    .error-text-container {
        height: 2rem;
        padding: 1rem;
    }

    .nowrap-cell {
        white-space: nowrap;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 0.25rem;
    }

    tr > td.action-col {
        padding: 0 1rem 0 1rem;

        .action-button-group {
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            align-items: center;
            width: 100%;
            .btn-icon {
                padding: 0.5rem;
                display: flex;
                flex-direction: column;
            }
        }
    }

    .table-toolbar-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        > * {
            flex: 1 1 0;
            height: 2.6rem;
        }
        :first-child {
            flex: 5 1 35ch;
        }
        button {
            border-radius: 0;
            border-width: 1px;
            border-style: solid;
            border-color: #dfdfe1;
        }
    }
}
</style>
