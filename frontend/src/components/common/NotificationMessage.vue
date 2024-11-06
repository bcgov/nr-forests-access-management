<script setup lang="ts">
import { ref, type VNode } from "vue";
import Message from "primevue/message";

import {
    clearNotification,
    showFullNotificationMsg,
} from "@/store/NotificationState";
import { IconSize } from "@/enum/IconEnum";
import type { SeverityType } from "@/enum/SeverityEnum";

const props = defineProps<{
    message: string | VNode | (() => VNode);
    severity: SeverityType;
    hasFullMsg?: boolean;
    hideSeverityText?: boolean;
    closable?: boolean;
}>();

const showSeeAll = ref(props.hasFullMsg);

const closeNotification = () => {
    clearNotification(props.severity);
};
</script>

<template>
    <div class="message-container">
        <Message
            icon="none"
            :class="props.severity"
            :severity="props.severity"
            :sticky="true"
            :closable="props.closable === undefined ? true : props.closable"
            @close="closeNotification()"
        >
            <Icon
                :icon="
                    props.severity === 'success'
                        ? 'checkmark--filled'
                        : props.severity === 'error'
                        ? 'misuse'
                        : 'warning--filled'
                "
                :size="IconSize.medium"
            />
            <span class="custom-message-text">
                <strong v-if="!hideSeverityText">{{ props.severity }}</strong>
                <span class="message-content">
                    <!-- Check message type and render accordingly -->
                    <component
                        :is="typeof message === 'function' ? message : null"
                        v-if="typeof message === 'function'"
                    />
                    <template v-else-if="typeof message === 'object'">
                        <!-- Render VNode directly -->
                        <component :is="message" />
                    </template>
                    <template v-else>
                        <!-- Render string message directly -->
                        {{ message }}
                    </template>
                </span>
                <button
                    v-if="hasFullMsg && showSeeAll"
                    class="btn-see-all"
                    @click="
                        () => {
                            showFullNotificationMsg(props.severity);
                            showSeeAll = false;
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
