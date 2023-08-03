<script setup inherit-attrs="false" lang="ts">
import Dialog from 'primevue/dialog';

const props = defineProps({
    error: {
        type: Boolean,
        default: false,
    },
    header: {
        type: String,
        required: true,
    },
    textFirst: {
        type: String,
        required: true,
    },
    textSecond: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <Dialog
        modal
        :header="props.header.toUpperCase()"
        :style="{ width: '50vw' }"
        class="modal-dialog"
        :class="{
            error: props.error,
        }"
    >
        <p
            :class="{
                error: props.error,
            }"
        >
            {{ props.textFirst }}
        </p>
        <p>{{ props.textSecond }}</p>
    </Dialog>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
.error {
    color: $text-error;
}
</style>
