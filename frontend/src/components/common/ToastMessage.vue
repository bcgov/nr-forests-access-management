<script setup lang="ts">
import { IconSize } from '@/enum/IconEnum';
import { app } from '@/main';
import {
    getToastErrorMsg,
    routeToastError,
    setRouteToastError,
    useToastService,
} from '@/store/ToastState';
import Toast, { type ToastMessageOptions } from 'primevue/toast';
import { watch } from 'vue';

const { showToastErrorTopRight } = useToastService();

app.config.errorHandler = (err) => {
    showToastErrorTopRight(getToastErrorMsg(err));
};

// Watch RouteError state change and popup toast if needed.
watch(routeToastError, (value) => {
    if (value) {
        showToastErrorTopRight(getToastErrorMsg(value));
    }
});

const handleToastTimeoutEnds = (message: ToastMessageOptions) => {
    setRouteToastError(undefined); // clear routeToastError state
};
</script>

<template>
    <Toast
        group="tl"
        position="top-right"
        #icon
        @life-end="handleToastTimeoutEnds"
    >
        <Icon
            icon="misuse"
            :size="IconSize.large"
            class="custom-carbon-icon-misuse"
        />
    </Toast>
</template>
