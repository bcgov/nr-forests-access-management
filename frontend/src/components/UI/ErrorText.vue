<script setup lang="ts">
import ErrorOutline from "@carbon/icons-vue/es/error--outline/16";

defineProps<{
    showIcon?: boolean;
    errorMsg?: string;
}>();
</script>
<template>
    <div class="error-text-container">
        <ErrorOutline v-if="showIcon" />
        <p v-if="errorMsg">{{ errorMsg }}</p>
    </div>
</template>
<style lang="scss" scoped>
.error-text-container {
    display: flex;
    flex-direction: row;
    align-items: center;

    p {
        margin: 0;
        color: var(--support-error);
    }

    svg {
        margin-right: 0.5rem;
        stroke: var(--support-error);
    }
}
</style>
