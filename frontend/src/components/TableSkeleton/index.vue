<script lang="ts" setup>
import Skeleton from 'primevue/skeleton';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

import type { ColumnType } from '@/types/TableTypes';

const props = defineProps<{
    headers: string[],
    rowAmount: number,
    className?: string,
}>();

// Create the columns array using headers
const columns: ColumnType[] = props.headers.map((header) => ({
    field: header,
    header: header,
}));

// Create placeholder rows for the skeleton table based on rowAmount
const skeletonRows = Array.from({ length: props.rowAmount }).map(() =>
    // Create a placeholder object with empty values for each column
    columns.reduce((acc, col) => {
        acc[col.field] = ''; // Set empty value for each column's field
        return acc;
    }, {} as Record<string, string>)
);

</script>

<template>
    <DataTable :class="props.className" :value="skeletonRows">
        <!-- Loop through the columns to render the headers and skeleton cells -->
        <Column v-for="col of columns" :key="col.field" :field="col.field" :header="col.header">
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
    </DataTable>
</template>
