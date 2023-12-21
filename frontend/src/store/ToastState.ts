import { ref } from 'vue';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';

// the toastError state is just used to store the error before enter the router
export const toastError = ref('');
export const setToastError = (error: string) => {
    toastError.value = error;
};
export const clearToastError = () => {
    toastError.value = '';
};

// the primevue toast can only be injected in setup or functional component,
// in order to reuse the toast service,
// we have to define it in the way as below
// https://stackoverflow.com/questions/72425297/vue-warn-inject-can-only-be-used-inside-setup-or-functional-components
export const useToastService = () => {
    const toast = useToast();

    const showToastErrorTopRight = (text: string) => {
        toast.add({
            severity: 'error',
            summary: 'ERROR',
            detail: text,
            group: 'tl',
        });
    };

    return { showToastErrorTopRight };
};

export const getToastErrorMsg = (error: any) => {
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
            return genericErrorMsg.text;
        } else if (status == 401) {
            return e401_authenticationErrorMsg.text;
        } else if (status == 403) {
            return e403_authorizationErrorMsg.text;
        } else if (status == 409) {
            return axiosResponse?.data.detail;
        }
        return;
    }
    return genericErrorMsg.text;
};

export const setToastErrorMsg = (error: any) => {
    setToastError(getToastErrorMsg(error));
};
