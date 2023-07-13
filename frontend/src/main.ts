import { createApp } from 'vue';
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';


import App from '@/App.vue';
import router from '@/router';

import 'bootstrap';

// import the fontawesome core
import { library } from '@fortawesome/fontawesome-svg-core';

// import font awesome icon component
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

// import specific icons
import { faTrashCan } from '@fortawesome/free-regular-svg-icons';

import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';


// use bootstrap4 as default style
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import 'primevue/resources/primevue.min.css';

import './assets/styles/styles.scss';
// add specific icons to library for use throughout application
library.add(faTrashCan);

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App);
app.use(ToastService);
app.use(ConfirmationService);

app.use(PrimeVue);
app.use(router).component('font-awesome-icon', FontAwesomeIcon).mount('#app');
export { app }