import { Amplify } from 'aws-amplify';
import { createApp } from 'vue';
import awsExports from './aws-exports';

import App from '@/App.vue';
import router from '@/router';

import 'bootstrap';

import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import ApiServiceFactory from '@/services/ApiServiceFactory';
import 'primevue/resources/primevue.min.css';
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import './assets/styles/styles.scss';

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App);
app.use(ToastService);
app.use(ConfirmationService);

// Global provided services.
const apiServiceProvider = new ApiServiceFactory();
app.provide(ApiServiceFactory.ADMIN_MANAGEMENT_API_SERVICE_KEY,
    apiServiceProvider.getAdminManagementApiService());
app.provide(ApiServiceFactory.APP_ACCESS_CONTROL_API_SERVICE_KEY,
    apiServiceProvider.getAppAccessControlApiService());

app.use(PrimeVue);
app.use(router).mount('#app');
export { app };
