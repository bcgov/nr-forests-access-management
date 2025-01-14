<script setup lang="ts">
defineProps<{
    title: string;
    description: string;
}>();
</script>

<template>
    <div class="table-title-container">
        <h3>
            {{ title }}
        </h3>
        <p>
            {{ description }}
        </p>
    </div>
</template>
<style lang="scss" scoped>
.table-title-container {
    min-height: 5.375rem;
    padding: 1rem 1rem 1.5rem 1rem;
    h3 {
        @include type.type-style("heading-03");
        color: var(--text-primary);
        margin: 0;
    }
    p {
        @include type.type-style("body-compact-01");
        color: var(--text-secondary);
        margin: 0;
    }
}
</style>
