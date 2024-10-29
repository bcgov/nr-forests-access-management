<script setup lang="ts">
import Chip from "primevue/chip";
defineProps<{
    label: string;
}>();
</script>

<template>
    <Chip class="fam-chip" :label="label" />
</template>

<style lang="scss">
.fam-chip {
    max-height: 1.5rem;
    background: colors.$blue-10;

    .p-chip-text {
        @include type.type-style("label-01");
        color: colors.$blue-80;
    }
}
</style>
