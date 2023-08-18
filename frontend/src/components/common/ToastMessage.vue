<script setup lang="ts">
import { app } from '@/main';
import axios from 'axios';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import { IconSize } from '@/enum/IconEnum';

import {
    useNotificationMessage,
    useErrorDialog,
} from '@/store/NotificationState';

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
        const status = axiosResponse?.status;

        const e401_authenticationErrorMsg = {
            title: 'Error',
            text: 'You are not logged in. Please log in.',
        };

        const e403_authorizationErrorMsg = {
            title: 'Error',
            text: 'You do not have the necessary authorization for the requested action.',
        };

        if (!status) {
            showToastTopRight(
                'error',
                genericErrorMsg.title,
                genericErrorMsg.text
            );
        } else if (status == 401) {
            showToastTopRight(
                'error',
                e401_authenticationErrorMsg.title,
                e401_authenticationErrorMsg.text
            );
        } else if (status == 403) {
            showToastTopRight(
                'error',
                e403_authorizationErrorMsg.title,
                e403_authorizationErrorMsg.text
            );
        } else if (status == 409) {
            useNotificationMessage.isNotificationVisible = false;
            useErrorDialog.dialogTitle = axiosResponse.statusText;
            useErrorDialog.dialogMsg = axiosResponse.data.detail;
            useErrorDialog.isErrorVisible = true;
        }
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
            :size=IconSize.large
            :class="'custom-carbon-icon-error--filled'"
        />
    </Toast>
</template>

