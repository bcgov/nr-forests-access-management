<script setup lang="ts">
import { watch } from "vue";
import { isAxiosError } from "axios";
import { useQuery } from "@tanstack/vue-query";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

import { router } from "@/router";
import TableSkeleton from "@/components/TableSkeleton";
import DateCol from "@/components/UserPermissionHistoryTable/DateCol.vue";
import PermissionDetailsCol from "@/components/UserPermissionHistoryTable/PermissionDetailsCol.vue";
import ChangePerformerCol from "@/components/UserPermissionHistoryTable/ChangePerformerCol.vue";

const props = defineProps<{
    userId: string;
    applicationId: string;
}>();

const auditHistoryQuery = useQuery({
    queryKey: [
        "permission-audit-history",
        { user_id: props.userId, application_id: props.applicationId },
    ],
    queryFn: () =>
        AppActlApiService.permissionAuditApi
            .getPermissionAuditHistoryByUserAndApplication(
                Number(props.userId),
                Number(props.applicationId)
            )
            .then((res) => res.data),
    enabled: !!props.userId && !!props.applicationId,
    staleTime: 0,
    gcTime: 0,
});

// Navigate back if user has no permission to view data.
watch(
    () => auditHistoryQuery.error.value,
    (error) => {
        if (isAxiosError(error) && error.response?.status === 403) {
            router.push("/");
        }
    }
);

const headers = ["Date", "Activity", "Details", "Performed by"];
</script>

<template>
    <!-- Skeleton when data is loading -->
    <TableSkeleton
        class-name="user-permission-table"
        :headers="headers"
        :row-amount="5"
        v-if="auditHistoryQuery.isFetching.value"
    />

    <!-- Simple error display -->
    <div v-else-if="auditHistoryQuery.isError.value">
        Something went wrong.
        {{
            isAxiosError(auditHistoryQuery.error.value)
                ? `${auditHistoryQuery.error.value.status}: ${auditHistoryQuery.error.value.message}`
                : auditHistoryQuery.error.value
        }}
    </div>

    <!-- Table with values -->
    <DataTable
        class="user-permission-table"
        :value="auditHistoryQuery.data.value"
        :striped-rows="true"
        v-else
    >
        <template #empty> No User Permissions History found.</template>
        <Column field="create_date" :header="headers[0]">
            <template #body="slotProps">
                <DateCol :utc-date="slotProps.data.create_date" />
            </template>
        </Column>
        <Column
            class="privilege-type-description-col"
            field="privilege_change_type_description"
            :header="headers[1]"
        />
        <Column field="privilege_details" :header="headers[2]">
            <template #body="slotProps">
                <PermissionDetailsCol
                    :permission-details="slotProps.data.privilege_details"
                    :permission-change-type="
                        slotProps.data.privilege_change_type_code
                    "
                />
            </template>
        </Column>
        <Column field="change_performer_user_details" :header="headers[3]">
            <template #body="slotProps">
                <ChangePerformerCol
                    :performer-details="
                        slotProps.data.change_performer_user_details
                    "
                />
            </template>
        </Column>
    </DataTable>
</template>

<style lang="scss">
.user-permission-table {
    table {
        /* Header Corners */
        th:first-child {
            border-top-left-radius: 0.5rem;
            /* Top-left corner */
        }

        th:last-child {
            border-top-right-radius: 0.5rem;
            /* Top-right corner */
        }

        /* Bottom Corners */
        tr:last-child td:first-child {
            border-bottom-left-radius: 0.5rem;
            /* Bottom-left corner */
        }

        tr:last-child td:last-child {
            border-bottom-right-radius: 0.5rem;
            /* Bottom-right corner */
        }
    }

    /* Table Row and Cell Styling */
    .p-datatable-tbody > tr > td {
        padding: 1rem;
    }

    /* Table Header Styling */
    .p-datatable-thead > tr > th {
        background: colors.$gray-20;
        height: 4rem;
    }

    /* Column Header Content */
    .p-column-header-content .p-column-title {
        padding: 1rem 0;
    }

    /* Privilege Type Column */
    .privilege-type-description-col {
        white-space: nowrap;
    }

    /* Footer Styling */
    .p-datatable-footer {
        border: none;

        .footer-text {
            @include type.type-style("body-compact-01");
            display: flex;
            flex-direction: row;
            justify-content: center;
        }
    }

    /* Hover Effects */
    .p-datatable-tbody > tr:hover {
        background-color: inherit;
        /* Retains the original color of the row */
    }

    .p-datatable-tbody > tr:nth-child(even):hover {
        background-color: var(--primevue-striped-row-color);
    }

    .p-datatable-tbody > tr:nth-child(odd):hover {
        background-color: colors.$white;
    }

    /* Paragraphs inside the Table */
    p {
        margin: 0;
    }
}
</style>
