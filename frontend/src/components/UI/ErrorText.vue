<script setup lang="ts">
import WarnOutline from "@carbon/icons-vue/es/warning--filled/16";

defineProps<{
    showIcon?: boolean;
    errorMsg?: string;
}>();
</script>
<template>
    <div class="error-text-container">
        <WarnOutline v-if="showIcon" />
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
        color: var(--text-error);
    }

    svg {
        margin-right: 0.5rem;
        fill: var(--support-error);
    }
}
</style>
