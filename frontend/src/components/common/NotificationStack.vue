<script setup lang="ts">
import { notifications } from '@/store/NotificationState';
</script>

<template>
    <TransitionGroup name="fade" tag="div">
        <template v-for="(value, key) in notifications" :key="key">
            <NotificationMessage
                v-if="value.msg !== ''"
                :severity="key.toString()"
                :msg-text="value.msg"
                :hasFullMsg="value.fullMsg !== ''"
                class="notification-stack"
            />
        </template>
    </TransitionGroup>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.notification-stack {
    padding-bottom: 1rem;
    &:deep(.p-message) {
        position: relative;
        margin-bottom: -1rem;
    }
}

/* ----- fade animation styles ----- */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
    opacity: 0;
}
</style>
