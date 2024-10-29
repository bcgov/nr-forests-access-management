<script setup lang="ts">
import { ref } from "vue";
import { FilterMatchMode } from "primevue/api";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { useQuery } from "@tanstack/vue-query";
import type { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import RecentlyViewedIcon from "@carbon/icons-vue/es/recently-viewed/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";

import {
    getTableHeaderDescription,
    getTableHeaderTitle,
    getGrantButtonLabel,
    filterList,
} from "@/components/managePermissions/utils";
import TableToolbar from "@/components/Table/TableToolbar.vue";
import TableHeaderTitle from "@/components/managePermissions/TableHeaderTitle.vue";
import Chip from "@/components/UI/Chip.vue";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { formatUserNameAndId } from "@/utils/UserUtils";

const props = defineProps<{
    authGroup: AdminRoleAuthGroup;
    appName: string;
    appId: number;
}>();

const appAdminQuery = useQuery({
    queryKey: ["application_admins"],
    queryFn: () =>
        AdminMgmtApiService.applicationAdminApi
            .getApplicationAdmins()
            .then((res) => res.data),
    refetchOnMount: true,
    enabled: props.authGroup === "FAM_ADMIN",
});

const appUserQuery = useQuery({
    queryKey: ["fam_applications", props.appId, "user_role_assignment"],
    queryFn: () =>
        AppActlApiService.applicationsApi
            .getFamApplicationUserRoleAssignment(props.appId)
            .then((res) => res.data),
    refetchOnMount: true,
    enabled: props.authGroup === "APP_ADMIN",
});

const delegatedAdminQuery = useQuery({
    queryKey: ["access_control_privileges", { application_id: props.appId }],
    queryFn: () =>
        AdminMgmtApiService.delegatedAdminApi
            .getAccessControlPrivilegesByApplicationId(props.appId)
            .then((res) => res.data),
    refetchOnMount: true,
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
</script>

<template>
    <div class="fam-table">
        <TableHeaderTitle
            :title="getTableHeaderTitle(appName, authGroup)"
            :description="getTableHeaderDescription(appName, authGroup)"
        />

        <TableToolbar
            :filter="tableFilter['global'].value"
            :btn-label="getGrantButtonLabel(authGroup)"
            :btn-on-click="() => {}"
            input-placeholder="Search by keyword"
            @change="handleSearchChange"
        />

        <DataTable
            :value="getTableRows()"
            removableSort
            stripedRows
            v-model:filters="tableFilter"
            filterDisplay="menu"
            :globalFilterFields="filterList"
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
                                : data.role.parent_role
                                ? data.role.parent_role.role_name
                                : data.role.display_name
                        "
                    />
                </template>
            </Column>

            <Column header="Action">
                <template #body>
                    <button
                        v-if="authGroup !== 'FAM_ADMIN'"
                        title="User permission history"
                        class="btn btn-icon"
                        @click="() => {}"
                    >
                        <RecentlyViewedIcon />
                    </button>

                    <button
                        title="Delete user"
                        class="btn btn-icon"
                        @click="() => {}"
                    >
                        <TrashIcon />
                    </button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
<style lang="scss" scoped>
.table-title-container {
}
</style>
