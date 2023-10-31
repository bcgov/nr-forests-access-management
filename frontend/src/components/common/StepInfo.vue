<script setup lang="ts">
const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="group">
        <h1 class="title">{{ props.title }}</h1>
        <h2 class="subtitle">{{ props.subtitle }}</h2>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
.group {
    padding: 0 !important;
    margin-bottom: 2.5rem;
}
.title {
    font-size: 1.25rem;
    line-height: 1.75rem; /* 140% */
    color: $light-text-primary;
    font-weight: 400;
}

.subtitle {
    font-size: 0.875rem;
    line-height: 1.125rem;
    letter-spacing: 0.01rem;
    color: $light-text-secondary;
}
</style>
