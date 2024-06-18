<script setup lang="ts">
import { ref } from 'vue';
import Message from 'primevue/message';

import {
    clearNotification,
    showFullNotificationMsg,
} from '@/store/NotificationState';
import { IconSize } from '@/enum/IconEnum';
import type { Severity } from '@/enum/SeverityEnum';

const props = defineProps({
    msgText: {
        type: String,
        required: true,
    },
    severity: {
        type: String,
        required: true,
    },
    hasFullMsg: {
        type: Boolean,
        required: false,
    },
});

const showSeeAll = ref(props.hasFullMsg as boolean);

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
                        ? 'misuse'
                        : 'warning--filled'
                "
                :size="IconSize.medium"
            />
            <span class="custom-message-text">
                <strong>{{ props.severity }}</strong>
                {{ props.msgText }}
                <button
                    v-if="hasFullMsg && showSeeAll"
                    class="btn-see-all"
                    @click="() => {
                        showFullNotificationMsg(props.severity as Severity);
                        showSeeAll = false
                    }"
                >
                    See all
                </button>
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