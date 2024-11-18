<script setup lang="ts">
import Chip from "primevue/chip";
const props = defineProps<{
    label: string;
    color?: "blue" | "green";
}>();

const customColorClass =
    props.color === "green" ? "fam-chip-green" : "fam-chip-blue";
</script>

<template>
    <Chip :class="`fam-chip ${customColorClass}`" :label="label" />
</template>

<style lang="scss">
.fam-chip {
    width: fit-content;
    height: 1.5rem;
    min-height: fit-content;
    display: flex;
    flex-direction: row;
    justify-content: center;

    .p-chip-text {
        @include type.type-style("label-01");
        text-align: center;
    }
}

.fam-chip-blue {
    background: colors.$blue-10;
    .p-chip-text {
        color: colors.$blue-80;
    }
}

.fam-chip-green {
    background: colors.$green-10;
    .p-chip-text {
        color: colors.$green-80;
    }
}
</style>
