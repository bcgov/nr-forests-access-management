<script setup lang="ts">
import { utcToLocalDateTime } from "@/utils/DateUtils";

const props = defineProps<{
    utcDate: string;
}>();
</script>

<template>
    <p className="table-date-column">{{ utcToLocalDateTime(props.utcDate) }}</p>
</template>

<style lang="scss" scoped>
.table-date-column {
    white-space: nowrap;
}
</style>
