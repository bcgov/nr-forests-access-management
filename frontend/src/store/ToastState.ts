import { ref } from 'vue';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';

// we use toast just for backend api errors
export const toastError = ref('');
export const setToastError = (error: string) => {
    toastError.value = error;
};
export const clearToastError = () => {
    toastError.value = '';
};

export const showToastErrorTopRight = (text: string) => {
    useToast().add({
        severity: 'error',
        summary: 'ERROR',
        detail: text,
        group: 'tl',
    });
};

export const onError = (error: any) => {
    console.error(`Error occurred: ${error.toString()}`);

    const genericErrorMsg = {
        title: 'Error',
        text: 'An application error has occurred. Please try again. If the error persists contact support.',
    };

    // Axios Http instance error that we like to pop out additional toast message.
    if (axios.isAxiosError(error)) {
        const axiosResponse = error.response;
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
            setToastError(genericErrorMsg.text);
        } else if (status == 401) {
            setToastError(e401_authenticationErrorMsg.text);
        } else if (status == 403) {
            setToastError(e403_authorizationErrorMsg.text);
        } else if (status == 409) {
            setToastError(axiosResponse?.data.detail);
        }
        return;
    }
    setToastError(genericErrorMsg.text);
};
