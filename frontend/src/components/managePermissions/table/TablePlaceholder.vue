<script setup lang="ts">
import { IconSize } from '@/enum/IconEnum';
</script>

<template>
    <div class="no-app-selected">
        <Icon
            role="presentation"
            icon="search--locate"
            :size="IconSize.small"
            class="icon-color"
            title="Search-locate Icon"
        />
        <p class="no-app-selected-title">Nothing to show yet!</p>
        <p class="no-app-selected-text">
            Choose an application to show a list of users with access to it. The
            list will display here.
        </p>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.no-app-selected {
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 21.745rem);
    min-height: 12.5rem;
    margin: 0 5rem;

    SVG {
        width: 3rem;
        height: 3rem;
    }
}

.no-app-selected-title {
    padding-top: 1rem;
    font-size: 1rem;
    font-weight: 700;
}

.no-app-selected-text {
    font-size: 0.875rem;
    color: $light-text-secondary;
    margin-bottom: 0 !important;
}

.icon-color {
    color: $light-background-brand;
}
</style>
