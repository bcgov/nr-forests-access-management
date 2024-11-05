<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import { computed } from "vue";

const props = defineProps<{
    ariaLabel?: string;
    loadingText?: string;
    isWhite?: boolean;
    small?: boolean;
}>();

const spinnerClass = computed(() => ({
    "small-spinner": props.small,
    "white-spinner": props.isWhite,
}));
</script>

<template>
    <div class="spinner-container">
        <ProgressSpinner
            :class="['default-loading-spinner', spinnerClass]"
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

    .small-spinner {
        width: 1rem; // Smaller size if "small" is true
    }

    .white-spinner .p-progress-spinner-svg circle {
        stroke: colors.$white; // White color if "isWhite" is true
    }

    .loading-text {
        margin-top: 1rem;
    }
}
</style>
