import { createApp } from 'vue';
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';


import App from '@/App.vue';
import router from '@/router';

import 'bootstrap';
// use bootstrap4 as default style
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import './assets/styles/styles.scss';

import ConfirmationService from 'primevue/confirmationservice';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App);
app.use(ToastService);
app.use(ConfirmationService);

app.use(PrimeVue);
app.use(router)
app.mount('#app');
export { app }