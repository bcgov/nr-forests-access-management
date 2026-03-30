<script setup lang="ts">
import NotificationMessage from "@/components/UI/NotificationMessage.vue";
import type { PermissionNotificationType } from "@/types/NotificationTypes";

defineProps<{
    permissionNotifications: PermissionNotificationType[];
    onClose: Function;
}>();
</script>

<template>
    <TransitionGroup name="fade" tag="div">
        <template
            v-for="(value, index) in permissionNotifications"
            :key="index"
        >
            <NotificationMessage
                :severity="value.severity"
                :message="value.message"
                :has-full-msg="value.hasFullMsg"
                :full-message="value.fullMessage"
                class="notification-stack"
                :on-close="() => onClose(index)"
                closable
            />
        </template>
    </TransitionGroup>
</template>

<style lang="scss" scoped>
@use "@/assets/styles/styles";

.notification-stack {
    margin-bottom: 1rem;

    &:deep(.p-message) {
        position: relative;
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
