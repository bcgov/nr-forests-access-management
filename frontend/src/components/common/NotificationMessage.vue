<script setup lang="ts">
import Message from 'primevue/message';
import { IconSize } from '@/enum/IconEnum';

import { clearNotification } from '@/store/NotificationState';

const props = defineProps({
    msgText: {
        type: String,
        required: true,
    },
    severity: {
        type: String,
        required: true,
    },
});

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
            @close="closeNotification()"
        >
            <Icon
                :icon="
                    props.severity === 'success'
                        ? 'checkmark--filled'
                        : props.severity === 'error'
                        ? 'error--filled'
                        : 'warning--filled'
                "
                :size="IconSize.medium"
            />
            <span class="custom-message-text">
                <strong>{{ props.severity }}</strong> {{ props.msgText }}
            </span>
        </Message>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.message-container {
    position: relative;
    align-items: center;
}

.custom-message-text {
    color: $light-text-primary;
}
</style>
