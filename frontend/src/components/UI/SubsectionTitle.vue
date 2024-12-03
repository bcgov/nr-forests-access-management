<script setup lang="ts">
defineProps<{
    title: string;
    subtitle?: string;
}>();
</script>

<template>
    <div class="subsection-title-container">
        <span class="subsection-title">{{ title }}</span>
        <p v-if="subtitle" class="subsection-subtitle">
            {{ subtitle }}
        </p>
    </div>
</template>

<style lang="scss">
.subsection-title-container {
    .subsection-title {
        @include type.type-style("heading-01");
        color: var(--text-primary);
    }

    .subsection-subtitle {
        @include type.type-style("body-01");
        color: var(--text-secondary);
    }
}
</style>
