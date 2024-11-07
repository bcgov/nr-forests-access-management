<script setup lang="ts">
import Button from "primevue/button";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import { type Component } from "vue";
import Spinner from "@/components/UI/Spinner.vue";

const props = defineProps<{
    label: string;
    name: string;
    // The current styles does not support all kinds, add your own if needed
    kind?: "primary" | "secondary" | "danger" | "primary-tertiary";
    link?: boolean;
    ariaLabel?: string;
    isLoading?: boolean;
    disabled?: boolean;
    icon?: Component;
    iconPos?: "left" | "right"; // affects loading icon only
}>();

// Define emits for 'click'
const emit = defineEmits<{
    (e: "click", event: MouseEvent | KeyboardEvent): void;
}>();

// Function to handle the Enter key press
const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
        emit("click", event);
    }
};

const kindClass = props.kind
    ? `fam-button-${props.kind}`
    : "fam-button-primary";
</script>
<template>
    <div :class="`${kindClass} fam-button`">
        <Button
            :name="name"
            :label="label"
            :loading="isLoading"
            @click="(event) => emit('click', event)"
            @keydown="handleKeyDown"
            :disabled="disabled"
            :icon-pos="iconPos ?? 'right'"
        >
            <component
                :is="icon || SearchLocateIcon"
                class="button-icon"
                v-if="iconPos === 'left' && !isLoading"
            />

            <Spinner v-if="isLoading && iconPos === 'left'" small />

            <span class="button-label">{{ label }}</span>

            <component
                :is="icon || SearchLocateIcon"
                class="button-icon"
                v-if="iconPos !== 'left' && !isLoading"
            />
            <Spinner v-if="isLoading && iconPos !== 'left'" small />
        </Button>
    </div>
</template>
<style lang="scss">
.fam-button {
    .p-button {
        white-space: nowrap;
        min-width: fit-content;
        height: 2.5rem;
        width: 7.875rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }

    .button-label {
        @include type.type-style("body-compact-02");
    }

    .button-icon {
        width: 1rem;
        height: 1rem;
    }
}

.fam-button-primary-tertiary {
    .p-button {
        border: 0.0625rem solid colors.$blue-70;
        background-color: transparent;
        color: colors.$blue-70;

        .p-progress-spinner-svg circle {
            stroke: colors.$blue-70;
        }
    }

    .p-button:hover {
        border-color: colors.$blue-75;
        background-color: colors.$blue-75;
        color: colors.$white;

        .p-progress-spinner-svg circle {
            stroke: colors.$white;
        }
    }

    .p-button:active {
        border-color: colors.$blue-80;
        background-color: colors.$blue-80;
        color: colors.$white;

        .p-progress-spinner-svg circle {
            stroke: colors.$white;
        }
    }

    .p-button:focus {
        border-color: colors.$blue-60;
        background-color: colors.$blue-60;
        color: colors.$white;

        .p-progress-spinner-svg circle {
            stroke: colors.$white;
        }
    }
}
</style>
