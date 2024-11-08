<script setup lang="ts">
import NotificationMessage from "./NotificationMessage.vue";
import type { PermissionNotificationType } from "@/types/ManagePermissionsTypes";

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
                :severity="value.serverity"
                :message="value.message"
                :has-full-msg="value.hasFullMsg"
                :full-message="value.fullMessage"
                class="notification-stack"
                :on-close="() => onClose(index)"
            />
        </template>
    </TransitionGroup>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/styles.scss";
.notification-stack {
    margin-bottom: 1.5rem;

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
