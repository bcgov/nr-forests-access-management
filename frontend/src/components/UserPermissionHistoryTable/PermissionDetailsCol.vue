<script setup lang="ts">
import { utcToTableLocalDateTime } from '@/utils/DateUtils';

const props = defineProps<{
    permission: string;
}>();
</script>

<template>
    <p className="table-date-column">{{ utcToTableLocalDateTime(props.utcDate) }}</p>
</template>

<style lang="scss" scoped>

</style>
