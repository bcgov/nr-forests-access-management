<script lang="ts" setup>
import Skeleton from "primevue/skeleton";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

import type { ColumnType } from "@/types/TableTypes";

const props = defineProps<{
    headers: string[];
    rowAmount: number;
    className?: string;
}>();

// Create the columns array using headers
const columns: ColumnType[] = props.headers.map((header) => ({
    field: header,
    header: header,
}));

// Create placeholder rows for the skeleton table based on rowAmount
const skeletonRows = Array.from({ length: props.rowAmount }, () =>
    Object.fromEntries(columns.map((col) => [col.field, ""]))
);
</script>

<template>
    <DataTable
        :class="
            'fam-table-skeleton' +
            (props.className ? ` ${props.className}` : '')
        "
        :value="skeletonRows"
    >
        <!-- Loop through the columns to render the headers and skeleton cells -->
        <Column
            v-for="col of columns"
            :key="col.field"
            :field="col.field"
            :header="col.header"
        >
            <template #body>
                <Skeleton width="100%" height="1.5rem" />
            </template>
        </Column>
    </DataTable>
</template>

<style lang="scss">
.fam-table-skeleton {
    .p-datatable-tbody > tr:hover {
        background-color: transparent;
    }
}
</style>
