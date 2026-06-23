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
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.5rem;

    .p-chip-label {
        @include type.type-style("label-01");
        text-align: center;
    }
}

.fam-chip-blue.p-chip {
    background: colors.$blue-10;
    .p-chip-label {
        color: colors.$blue-80;
    }
}

.fam-chip-green.p-chip {
    background: colors.$green-10;
    .p-chip-label {
        color: colors.$green-80;
    }
}

</style>
