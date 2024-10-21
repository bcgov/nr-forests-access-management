<script setup lang="ts">
// The default loading spinner.
import ProgressSpinner from "primevue/progressspinner";

defineProps<{
    ariaLabel?: string;
    loadingText?: string;
}>();
</script>

<template>
    <div class="spinner-container">
        <ProgressSpinner
            class="default-loading-spinner"
            :aria-label="ariaLabel ?? 'Page Loading'"
            animationDuration="1s"
            stroke-width="3"
        />
        <h5 v-if="loadingText" class="loading-text">{{ loadingText }}</h5>
    </div>
</template>

<style lang="scss">
.spinner-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    .default-loading-spinner {
        .p-progress-spinner-svg circle {
            stroke: colors.$blue-60;
            animation: none;
        }
    }

    .loading-text {
        margin-top: 1rem;
    }
}
</style>
