<script setup lang="ts">
import { notifications } from '@/store/NotificationState';
</script>

<template>
    <div v-for="(value, key) in notifications">
        <NotificationMessage
            v-if="value.msg !== ''"
            :severity="key.toString()"
            :msg-text="value.msg"
            :hasFullMsg="value.fullMsg !== ''"
            class="notification-stack"
        />
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.notification-stack {
    margin: 0rem 2.5rem;
    padding-bottom: 1rem;
    &:deep(.p-message) {
        position: relative;
        margin-bottom: -1rem;
    }
}
</style>
