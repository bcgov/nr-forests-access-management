<script setup lang="ts">
import Divider from "@/components/UI/Divider.vue";

defineProps<{
    title: string;
    subtitle?: string;
    divider?: boolean;
}>();
</script>

<template>
    <div class="step-container">
        <h2 class="title">{{ title }}</h2>
        <p v-if="subtitle" class="subtitle" aria-roledescription="subtitle">
            {{ subtitle }}
        </p>
        <div :class="subtitle ? 'step-content' : ''">
            <slot />
        </div>
        <Divider v-if="divider" />
    </div>
</template>

<style lang="scss">
.step-container {
    .step-content {
        margin-top: 1.5rem;
    }

    .title {
        font-size: 1.25rem;
        line-height: 1.75rem;
        color: var(--text-primary);
        font-weight: 400;
    }

    .subtitle {
        font-size: 0.875rem;
        line-height: 1.125rem;
        letter-spacing: 0.01rem;
        color: var(--text-secondary);
    }
}
</style>
