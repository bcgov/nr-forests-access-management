import { Amplify } from 'aws-amplify';
import { createApp } from 'vue';
import awsExports from './aws-exports';

import App from '@/App.vue';
import { historyRouter, hashRouter } from '@/router';  // Import the two routers

import 'bootstrap';

import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { isAxiosError } from 'axios';

import 'primevue/resources/primevue.min.css';
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import './assets/styles/styles.scss';

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

// Create the QueryClient instance with default options
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnMount: false,
            refetchOnWindowFocus: false,
            retry: (failureCount, error) => {
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
        }
    }
});

const app = createApp(App);
app.use(ToastService);
app.use(ConfirmationService);
app.use(PrimeVue);
app.use(VueQueryPlugin, { queryClient });

// Determine which router to use based on the initial path
const currentPath = window.location.pathname;
if (currentPath.startsWith('/authCallback')) {
    app.use(historyRouter);
} else {
    app.use(hashRouter);
}

app.mount('#app');
export { app };
