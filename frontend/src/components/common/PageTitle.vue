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
    <h1 class="title">{{ props.title }}</h1>
    <h2 class="subtitle">{{ props.subtitle }}</h2>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
.title {
    font-size: 2rem;
    line-height: 2.5rem;
    color: $text-primary;
}

.subtitle {
    font-size: .875rem;
    line-height: 1.125rem;
    letter-spacing: .01rem;
    color: $text-secondary;
}
</style>
