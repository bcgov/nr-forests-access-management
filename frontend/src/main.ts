import { createApp } from "vue";
import { Amplify } from "aws-amplify";
import amplifyconfig from "./amplifyconfiguration";
import App from "@/App.vue";
import { router } from "@/router";

import PrimeVue from "primevue/config";
import { FamPrimeVuePreset } from "@/passthrough/primevue-preset";
import ConfirmationService from "primevue/confirmationservice";
import DialogService from "primevue/dialogservice";
import Tooltip from "primevue/tooltip";
import { VueQueryPlugin, QueryClient } from "@tanstack/vue-query";
import { isAxiosError } from "axios";
import { THREE_HOURS } from "@/constants/TimeUnits";
import {
    CONFIRM_DIALOG_PASS_THROUGH,
    DIALOG_PASS_THROUGH,
    DYNAMIC_DIALOG_PASS_THROUGH,
} from "@/passthrough/dialog/dialogPassThrough";
import { INPUT_PASS_THROUGH } from "@/passthrough/input/inputPassThrough";
import { BUTTON_PASS_THROUGH } from "@/passthrough/button/buttonPassThrough";
import { RADIO_BUTTON_PASS_THROUGH } from "@/passthrough/radiobutton/radioButtonPassThrough";
import { MESSAGE_PASS_THROUGH } from "@/passthrough/message/messagePassThrough";

// Configure Amplify
Amplify.configure(amplifyconfig);

// QueryClient retry logic extracted into a function
function retryQuery(failureCount: number, error: unknown): boolean {
    const MAX_RETRIES = 3;
    const HTTP_STATUS_TO_NOT_RETRY = [400, 401, 403, 404, 500];

    if (failureCount > MAX_RETRIES) {
        return false;
    }
    if (isAxiosError(error)) {
        const status = error.response?.status;
        if (status && HTTP_STATUS_TO_NOT_RETRY.includes(status)) {
            return false;
        }
    }
    return true;
}

// Create the QueryClient instance
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnMount: false,
            refetchOnWindowFocus: false,
            retry: retryQuery,
            staleTime: THREE_HOURS,
            gcTime: THREE_HOURS,
        },
    },
});

// Create and configure the Vue app
const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: FamPrimeVuePreset,
    },
    pt: {
        dialog: DIALOG_PASS_THROUGH,
        dynamicdialog: DYNAMIC_DIALOG_PASS_THROUGH,
        confirmdialog: CONFIRM_DIALOG_PASS_THROUGH,
        inputtext: INPUT_PASS_THROUGH,
        button: BUTTON_PASS_THROUGH,
        radiobutton: RADIO_BUTTON_PASS_THROUGH,
        message: MESSAGE_PASS_THROUGH,
    },
});
app.use(ConfirmationService);
app.use(DialogService);
app.use(VueQueryPlugin, { queryClient });
app.directive("tooltip", Tooltip);

// Mount the app
app.mount("#app");

export { app };
