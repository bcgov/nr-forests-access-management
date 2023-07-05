<script setup lang="ts">
import Message from 'primevue/message';
defineProps<{
    msgText: string,
    severity: string
    icon: string
}>();
</script>

<template>
    <div class="message-container">
        <Message 
            icon="none"
            :class="severity"
            :severity="severity"
            :sticky=false
            :style="{
                color: '#131315'
            }"
        >
            <Icon :icon="icon" medium />
            <strong>{{ severity }}</strong> {{ msgText }}
        </Message>
    </div>
</template>

<style lang="scss" scoped>
@import '../../assets/styles/styles.scss';

svg {
    margin-right: 15px;
    margin-bottom: 5px;
}

strong {
    text-transform: capitalize;
}

.message-container {
border: solid 1px transparent;
margin-top: 40px;
}

:deep(.p-message.p-message-success .p-message-close) {
    color: #131315;
}

:deep(.p-message.p-message-success .p-message-close):focus {
    box-shadow: 0 0 0 0.1rem $support-success !important;
}

:deep(.p-message.p-message-success.success) {
    border: solid 1px $support-success !important;
    border-left: solid 5px rgba(0, 123, 0, 0.7) !important;
}

.p-message {
    margin-right: 80px;
    position: absolute;
    margin-right: 40px;
    // width: 100%;
}

</style>