<script setup lang="ts">
import {
    notifications,
    showFullNotificationMsg,
} from '@/store/NotificationState';
import { IconSize } from '@/enum/IconEnum';
import Message from 'primevue/message';
</script>

<template>
    <Message
        v-for="(value, key) in notifications"
        :key="value.severity"
        :class="`${value.severity} notification-stack `"
        :severity="value.severity"
        :sticky="true"
    >
        <Icon
            :icon="
                value.severity === 'success'
                    ? 'checkmark--filled'
                    : key.toString() === 'error'
                    ? 'misuse'
                    : 'warning--filled'
            "
            :size="IconSize.medium"
        />
        <span class="custom-message-text">
            <strong>{{ value.severity }}</strong>
            {{ value.msg }}
            <button
                v-if="value.showAll"
                class="btn-see-all"
                @click="
                    () => {
                        showFullNotificationMsg(value.severity);
                    }
                "
            >
                See all
            </button>
        </span>
    </Message>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.notification-stack {
    margin-bottom: 1rem;
    position: relative;
}
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
