<script setup lang="ts">
import Message from 'primevue/message';
import { IconSize } from '@/enum/IconEnum';

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
</script>

<template>
    <div class="message-container">
        <Message
            icon="none"
            :class="props.severity"
            :severity="props.severity"
            :sticky="true"
        >
            <Icon icon="checkmark--filled" :size="IconSize.medium" />
            <span class="message-text">
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

</style>
