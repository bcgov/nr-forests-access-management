import { Amplify } from 'aws-amplify';
import { createApp } from 'vue';
import awsExports from './aws-exports';

import App from '@/App.vue';
import { historyRouter, hashRouter } from '@/router';  // Import the two routers

import 'bootstrap';

import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import 'primevue/resources/primevue.min.css';
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import './assets/styles/styles.scss';

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App);
app.use(ToastService);
app.use(ConfirmationService);
app.use(PrimeVue);

// Determine which router to use based on the initial path
const currentPath = window.location.pathname;
if (currentPath.startsWith('/authCallback')) {
    app.use(historyRouter);
} else {
    app.use(hashRouter);
}

app.mount('#app');
export { app };
