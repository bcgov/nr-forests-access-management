<script setup lang="ts">
import CheckMarkIcon from "@carbon/icons-vue/es/checkmark--filled/20";
import MisuseIcon from "@carbon/icons-vue/es/misuse/20";
import WarnIcon from "@carbon/icons-vue/es/warning--filled/20";
import Message, { type MessageProps } from "primevue/message";
import { computed, ref, type VNode } from "vue";

// Define the properties, allowing `message` and `fullMessage` to support a VNode,
// a function that returns a VNode, or a string for flexible content rendering.
const props = defineProps<{
    message: string | VNode | (() => VNode);
    severity: MessageProps["severity"];
    hasFullMsg?: boolean;
    fullMessage?: string | VNode | (() => VNode);
    hideTitle?: boolean;
    closable?: boolean;
    onClose?: Function;
    title?: string;
}>();

const showAll = ref(false);

const displayMessage = computed(() => {
    if (showAll.value) {
        return props.fullMessage;
    } else {
        return props.message;
    }
});
</script>

<template>
    <div class="message-container">
        <Message
            icon="none"
            :class="props.severity"
            :severity="props.severity"
            :sticky="true"
            :closable="props.closable === undefined ? true : props.closable"
            @close="props.onClose ?? undefined"
        >
            <CheckMarkIcon v-if="props.severity === 'success'" />
            <MisuseIcon v-else-if="props.severity === 'error'" />
            <WarnIcon v-else />

            <span class="custom-message-text">
                <strong v-if="!hideTitle">{{
                    props.title ?? props.severity
                }}</strong>
                <!-- Render `displayMessage` based on its type -->
                <span class="message-content">
                    <!-- If `displayMessage` is a function, invoke it to get the VNode -->
                    <component
                        :is="
                            typeof displayMessage === 'function'
                                ? displayMessage
                                : null
                        "
                        v-if="typeof displayMessage === 'function'"
                    />
                    <!-- If `displayMessage` is a VNode object, render it directly -->
                    <template v-else-if="typeof displayMessage === 'object'">
                        <component :is="displayMessage" />
                    </template>
                    <template v-else>
                        <!-- Render string message directly -->
                        {{ displayMessage }}
                    </template>
                </span>
                <button
                    v-if="hasFullMsg && !showAll"
                    class="btn-see-all"
                    @click="
                        () => {
                            showAll = true;
                        }
                    "
                >
                    See all
                </button>
            </span>
        </Message>
    </div>
</template>

<style lang="scss" scoped>
@use "@/assets/styles/styles";
.message-container {
    position: relative;
    align-items: center;
    .p-message {
        position: inherit;
    }
}

.custom-message-text {
    color: var(--text-primary);
}

.btn-see-all {
    background-color: transparent;
    border: none;
    color: var(--link-primar);
    padding: 0;
}

.btn-see-all:hover {
    color: var(--link-primary-hover);
}
</style>
