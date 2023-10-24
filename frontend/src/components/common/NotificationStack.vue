<script setup lang="ts">
import { notifications } from '@/store/NotificationState';
</script>

<template>
    <div v-for="(value, key) in notifications">
        <NotificationMessage
            v-if="value.length > 0"
            :severity="key.toString()"
            :msg-text="value"
            class="notification-stack"
        />
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.notification-stack {
    margin: 0rem 2rem;
    padding-bottom: 1rem;
    &:deep(.p-message) {
        position: relative;
        margin-bottom: -1rem;
    }
}
</style>
