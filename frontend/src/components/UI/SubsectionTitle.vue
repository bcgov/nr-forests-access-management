<script setup lang="ts">
defineProps<{
    title: string;
    subtitle?: string;
}>();
</script>

<template>
    <div class="subsection-title-container">
        <span class="title">{{ title }}</span>
        <p v-if="subtitle" class="subtitle">
            {{ subtitle }}
        </p>
    </div>
</template>

<style lang="scss">
.subsection-title-container {
    .title {
        @include type.type-style("heading-01");
        color: var(--text-primary);
    }

    .subtitle {
        @include type.type-style("body-01");
        color: var(--text-secondary);
    }
}
</style>
