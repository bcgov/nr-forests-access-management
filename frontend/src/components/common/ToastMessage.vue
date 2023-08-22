<script setup lang="ts">
import { app } from '@/main';
import axios from 'axios';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import { IconSize } from '@/enum/IconEnum';

const toast = useToast();

const showToastTopRight = (sev: any, title: string, text: string) => {
    toast.add({ severity: sev, summary: title, detail: text, group: 'tl' });
};

const onError = (error: any, info: string) => {
    console.error(`Error occurred: ${error.toString()}`);
    const genericErrorMsg = {
        title: 'Error',
        text: 'An application error has occurred. Please try again. If the error persists contact support.',
    };

    // Axios Http instance error that we like to pop out additional toast message.
    if (axios.isAxiosError(error)) {
        const err = error;
        const axiosResponse = err.response;

        const axiosResponseHasDetail = axiosResponse?.data.detail
            ? axiosResponse.data.detail
            : genericErrorMsg.text;

        showToastTopRight(
            'error',
            axiosResponse ? axiosResponse.statusText : genericErrorMsg.title,
            axiosResponse?.data.detail.description
                ? axiosResponse.data.detail.description
                : axiosResponseHasDetail
        );
        return;
    }

    showToastTopRight('error', genericErrorMsg.title, genericErrorMsg.text);
};

app.config.errorHandler = (err, instance, info) => {
    onError(err, info);
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
