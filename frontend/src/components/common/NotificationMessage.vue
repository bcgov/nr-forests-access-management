<script setup lang="ts">
import Message from 'primevue/message';

const props = defineProps({
    msgText: {
        type: String,
        required: true,
    },
    severity: {
        type: String,
        required: true,
    },
    icon: {
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
            <Icon :icon="props.icon" medium />
            <span class="message-text">
                <strong>{{ props.severity }}</strong> {{ props.msgText }}
            </span>
        </Message>
    </div>
</template>

<style lang="scss" scoped>
@import '../../assets/styles/styles.scss';

svg {
    margin-right: 15px;
    vertical-align: middle;
}

strong {
    text-transform: capitalize;
}

.message-text {
    color: $text-primary;
}

.message-container {
    position: relative;
    align-items: center;
}

.p-message {
    position: absolute;
    left: 0;
    right: 0;
}
</style>
