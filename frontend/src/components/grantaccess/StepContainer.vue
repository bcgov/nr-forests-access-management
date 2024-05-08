<script setup lang="ts">
const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: false,
    },
    divider: {
        type: Boolean,
        default: true,
    },
});
</script>

<template>
    <div>
        <h2 class="title">{{ props.title }}</h2>
        <p v-if="subtitle" class="subtitle" aria-roledescription="subtitle">
            {{ props.subtitle }}
        </p>
        <div :class="subtitle ? 'step-content' : ''">
            <slot />
        </div>
        <Divider v-if="props.divider" />
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.step-content {
    margin-top: 1.5rem;
}
.title {
    font-size: 1.25rem;
    line-height: 1.75rem;
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
