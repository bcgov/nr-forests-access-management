<script setup lang="ts">
import { app } from '@/main';
import Toast from 'primevue/toast';
import { IconSize } from '@/enum/IconEnum';
import { getToastErrorMsg, useToastService } from '@/store/ToastState';

const { showToastErrorTopRight } = useToastService();

app.config.errorHandler = (err) => {
    showToastErrorTopRight(getToastErrorMsg(err));
};
</script>

<template>
    <Toast group="tl" position="top-right" #icon>
        <Icon
            icon="error--filled"
            :size="IconSize.large"
            class="custom-carbon-icon-error--filled"
        />
    </Toast>
</template>
