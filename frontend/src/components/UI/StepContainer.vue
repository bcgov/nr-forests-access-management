<script setup lang="ts">
import Divider from "@/components/UI/Divider.vue";

defineProps<{
    title?: string;
    subtitle?: string;
    divider?: boolean;
}>();
</script>

<template>
    <div class="step-container">
        <h3 v-if="title" class="title">{{ title }}</h3>
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
    container-type: inline-size; // Enables container queries for child components

    .step-content {
        margin-top: 1.5rem;
    }

    .title {
        @include type.type-style("heading-03");
        color: var(--text-primary);
    }

    .subtitle {
        @include type.type-style("body-01");
        color: var(--text-secondary);
    }
}
</style>
