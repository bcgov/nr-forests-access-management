<script setup lang="ts">
import { computed, ref, type VNode } from "vue";
import Message, { type MessageProps } from "primevue/message";
import CheckMarkIcon from "@carbon/icons-vue/es/checkmark--filled/20";
import MisuseIcon from "@carbon/icons-vue/es/misuse/20";
import WarnIcon from "@carbon/icons-vue/es/warning--filled/20";

const props = defineProps<{
    message: string | VNode | (() => VNode);
    severity: MessageProps["severity"];
    hasFullMsg?: boolean;
    fullMessage?: string | VNode | (() => VNode);
    hideSeverityText?: boolean;
    closable?: boolean;
    onClose?: Function;
}>();

const showAll = ref(false);

const displayMessage = computed(() => {
    if (showAll.value) {
        return props.fullMessage;
    } else {
        return props.message;
    }
});

const closeEvents = props.onClose ? { close: props.onClose } : {};
</script>

<template>
    <div class="message-container">
        <Message
            icon="none"
            :class="props.severity"
            :severity="props.severity"
            :sticky="true"
            :closable="props.closable === undefined ? true : props.closable"
            v-bind="closeEvents"
        >
            <CheckMarkIcon v-if="props.severity === 'success'" />
            <MisuseIcon v-else-if="props.severity === 'error'" />
            <WarnIcon v-else />

            <span class="custom-message-text">
                <strong v-if="!hideSeverityText">{{ props.severity }}</strong>
                <span class="message-content">
                    <!-- Render displayMessage based on type -->
                    <component
                        :is="
                            typeof displayMessage === 'function'
                                ? displayMessage
                                : null
                        "
                        v-if="typeof displayMessage === 'function'"
                    />
                    <template v-else-if="typeof displayMessage === 'object'">
                        <!-- Render VNode directly -->
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
@import "@/assets/styles/styles.scss";
.message-container {
    position: relative;
    align-items: center;
}

.custom-message-text {
    color: $light-text-primary;
}

.btn-see-all {
    background-color: transparent;
    border: none;
    color: $light-link-primary;
    padding: 0;
}

.btn-see-all:hover {
    color: $light-link-primary-hover;
}
</style>
