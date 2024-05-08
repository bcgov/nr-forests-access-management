import { FamRouteError, RouteErrorName } from '@/errors/FamCustomError';
import axios, { type AxiosError } from 'axios';
import { useToast } from 'primevue/usetoast';
import { ref } from 'vue';

// A RotetoastError state. Special case for handling routing error that
// cannot be caught from Vue.
export const routeToastError = ref();
export const setRouteToastError = (error: FamRouteError | AxiosError | undefined) => {
    routeToastError.value = error;
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
            life: 5000 // delay before auto cleared.
        });
    };

    return { showToastErrorTopRight };
};

const genericErrorMsg = {
    title: 'Error',
    text: 'An application error has occurred. Please try again. If the error persists contact support.',
};

export const getToastErrorMsg = (error: any) => {
    console.error(`Error occurred: ${error.toString()}`);

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

    if (error instanceof FamRouteError) {
        return handleRouteErrorMessage(error);
    }

    return genericErrorMsg.text;
};

const handleRouteErrorMessage = (error: FamRouteError): string => {
    if (RouteErrorName.NOT_AUTHENTICATED_ERROR == error.name ||
        RouteErrorName.NO_APPLICATION_SELECTED_ERROR == error.name ||
        RouteErrorName.ACCESS_RESTRICTED == error.name) {
        return error.message;
    }
    return genericErrorMsg.text;
}
