<script setup lang="ts">
import type { VNode } from "vue";

const props = defineProps<{
    text: string;
    isError?: boolean;
    id?: string;
}>();
</script>

<template>
    <p
        :class="props.isError ? 'fam-error-helper-text' : 'fam-helper-text'"
        :id="props.id"
    >
        {{ props.text }}
    </p>
</template>

<style lang="scss">
.fam-helper-text,
.fam-error-helper-text {
    @include type.type-style("label-01");
    padding: 0;
}

.fam-helper-text {
    color: var(--text-secondary);
}

.fam-error-helper-text {
    color: var(--text-error);
}
</style>
