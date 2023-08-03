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
    font-size: 32px;
    line-height: 40px;
    color: $text-primary;
}

.subtitle {
    font-size: 14px;
    line-height: 18px;
    letter-spacing: 0.16px;
    color: $text-secondary;
}
</style>
