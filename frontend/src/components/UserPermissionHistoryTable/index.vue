<script setup lang="ts">
import { isAxiosError } from 'axios';
import { useQuery } from '@tanstack/vue-query';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';


import TableSkeleton from '@/components/TableSkeleton';
import DateCol from '@/components/UserPermissionHistoryTable/DateCol.vue';
import PermissionDetailsCol from '@/components/UserPermissionHistoryTable/PermissionDetailsCol.vue';

const props = defineProps<{
    userId: string;
    applicationId: string
}>();

const auditHistoryQuery = useQuery(
    {
        queryKey: ['permission-audit-history', { user_id: props.userId, application_id: props.applicationId }],
        queryFn:
            () => AppActlApiService.permissionAuditApi
                .getPermissionAuditHistoryByUserAndApplication(
                    Number(props.userId), Number(props.applicationId)
                ).then((res) => res.data),
        enabled: !!props.userId && !!props.applicationId,
        staleTime: 0,
        gcTime: 0
    }
);

const headers = ['Date', 'Activity', 'Details', 'Performed by'];

</script>

<template>
    <!-- Skeleton when data is loading -->
    <TableSkeleton className="user-permission-table" :headers="headers" :row-amount="5"
        v-if="auditHistoryQuery.isFetching.value" />

    <!-- Table with values -->
    <DataTable class="user-permission-table" :value="auditHistoryQuery.data.value" v-else>
        <Column field="create_date" :header="headers[0]">
            <template #body="slotProps">
                <DateCol :utc-date="slotProps.data.create_date" />
            </template>
        </Column>
        <Column class="privilege-type-description-col" field="privilege_change_type_description" :header="headers[1]" />
        <Column field="privilege_details" :header="headers[2]">
            <template #body="slotProps">
                <PermissionDetailsCol :permission-details="slotProps.data.privilege_details" />
            </template>
        </Column>
        <Column field="change_performer_user_details" :header="headers[3]" />
    </DataTable>


</template>

<style lang="scss">
.user-permission-table {
    table {

        th:first-child {
            /* Top-left corner */
            border-top-left-radius: 0.5rem;
        }

        th:last-child {
            /* Top-right corner */
            border-top-right-radius: 0.5rem;
        }

        tr:last-child td:first-child {
            /* Bottom-left corner */
            border-bottom-left-radius: 0.5rem;
        }

        tr:last-child td:last-child {
            /* Bottom-right corner */
            border-bottom-right-radius: 0.5rem;
        }
    }

    p {
        margin: 0;
    }

    .p-datatable-tbody>tr>td {
        padding: 1rem;
    }

    .p-datatable-thead>tr>th {
        background: colors.$gray-20;
        height: 4rem;
    }

    .p-column-header-content .p-column-title {
        padding: 1rem 0;
    }

    .privilege-type-description-col {
        white-space: nowrap;
    }
}
</style>
