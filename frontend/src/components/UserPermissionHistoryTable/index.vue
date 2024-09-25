<script setup lang="ts">
import { isAxiosError } from 'axios';
import { useQuery } from '@tanstack/vue-query';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Skeleton from 'primevue/skeleton';

import DateCol from '@/components/UserPermissionHistoryTable/DateCol.vue';

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

</script>

<template>
    <!-- Skeleton when data is loading -->
    <DataTable class="user-permission-table" :value="[1, 2, 3, 4, 5]" v-if="auditHistoryQuery.isFetching.value">
        <Column field="create_date" header="Date">
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
        <Column field="privilege_change_type_code" header="Activity">
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
        <Column field="privilege_details" header="Details">
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
        <Column field="change_performer_user_details" header="Performed by">
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
    </DataTable>

    <DataTable class="user-permission-table" :value="auditHistoryQuery.data.value" v-else>
        <Column field="create_date" header="Date">
            <template #body="slotProps">
                <DateCol :utcDate="slotProps.data.create_date" />
            </template>
        </Column>
        <Column field="privilege_change_type_code" header="Activity" />
        <Column field="privilege_details" header="Details" />
        <Column field="change_performer_user_details" header="Performed by" />
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
}
</style>
