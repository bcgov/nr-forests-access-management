<script setup lang="ts">
import Button, { type ButtonProps } from "primevue/button";
import { type Component } from "vue";
import Spinner from "@/components/UI/Spinner.vue";

const props = defineProps<{
    label?: string;
    name?: string;
    severity?: ButtonProps["severity"];
    outlined?: boolean;
    link?: boolean;
    ariaLabel?: string;
    isLoading?: boolean;
    disabled?: boolean;
    icon?: Component;
    iconPos?: "left" | "right"; // affects loading icon only
    type?: "button" | "submit" | "reset";
    text?: boolean;
    iconOnly?: boolean;
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
</script>
<template>
    <Button
        :class="iconOnly ? 'fam-icon-button' : 'fam-button'"
        :severity="severity"
        :type="type ?? 'button'"
        :name="name ?? label"
        :label="label"
        :loading="isLoading"
        @click="(event) => emit('click', event)"
        @keydown="handleKeyDown"
        :disabled="disabled"
        :icon-pos="iconPos ?? 'right'"
        :aria-label="ariaLabel ?? label"
        :outlined="outlined"
        :text="text"
    >
        <div class="button-content" v-if="iconOnly">
            <component :is="icon" class="button-icon" />
        </div>
        <div class="button-content" v-else>
            <component
                :is="icon"
                class="button-icon"
                v-if="icon && iconPos === 'left' && !isLoading"
            />

            <Spinner v-if="isLoading && iconPos === 'left'" small />

            <span v-if="label" class="button-label">{{ label }}</span>

            <component
                :is="icon"
                class="button-icon"
                v-if="icon && iconPos !== 'left' && !isLoading"
            />
            <Spinner v-if="isLoading && iconPos !== 'left'" small />
        </div>
    </Button>
</template>
<style lang="scss">
.fam-button {
    white-space: nowrap;
    min-width: fit-content;
    height: 2.5rem;
    width: 7.875rem;
    display: flex;
    flex-direction: row;
    justify-content: space-between;

    .button-content {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        .button-label {
            @include type.type-style("body-compact-02");
        }

        .button-icon {
            width: 1rem;
            height: 1rem;
        }
    }
}

.p-button.fam-icon-button {
    background-color: colors.$white;
    border: none;

    svg {
        fill: var(--icon-primary);
    }
}

.p-button.fam-icon-button:enabled:hover {
    background-color: var(--background-hover);
}

.p-button.fam-icon-button:enabled:focus {
    background-color: var(--background-active);
}
</style>
