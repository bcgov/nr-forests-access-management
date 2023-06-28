import { createApp } from 'vue';
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';
import { vfmPlugin } from 'vue-final-modal';
import Toast, {
    POSITION,
    TYPE,
    useToast,
    type PluginOptions,
} from 'vue-toastification';
import 'vue-toastification/dist/index.css';

import App from '@/App.vue';
import router from '@/router';

import 'bootstrap';

import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';

// import the fontawesome core
import { library } from '@fortawesome/fontawesome-svg-core';

// import font awesome icon component
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

// import specific icons
import { faTrashCan } from '@fortawesome/free-regular-svg-icons';
import ErrorService from './services/ErrorService';

import PrimeVue from 'primevue/config';

// use bootstrap4 as default style
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import 'primevue/resources/primevue.min.css';

import './assets/styles/styles.scss';

// add specific icons to library for use throughout application
library.add(faTrashCan);

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App);

const toastOptions: PluginOptions = {
    // // Defaults for all toast messages
    position: POSITION.TOP_RIGHT,
    timeout: 5000, // milliseconds
    newestOnTop: true,

    // Prevent having multiple messages with the same type and content from being displayed.
    filterBeforeCreate: (toast, toasts) => {
        if (
            toasts.filter(
                (t) => t.type === toast.type && t.content === toast.content
            ).length !== 0
        ) {
            // Returning false discards the toast
            return false;
        }
        return toast;
    },
    toastDefaults: {
        // ToastOptions object for each type of toast
        [TYPE.ERROR]: {
            position: POSITION.TOP_CENTER,
            timeout: 5000,
        },
        [TYPE.SUCCESS]: {
            position: POSITION.TOP_RIGHT,
            timeout: 4000,
        },
        [TYPE.WARNING]: {
            position: POSITION.TOP_RIGHT,
            timeout: 4000,
        },
    },
};
app.use(Toast, toastOptions);

app.use(
    vfmPlugin({
        key: '$vfm',
        componentName: 'VueFinalModal',
        dynamicContainerName: 'ModalsContainer',
    })
);

app.config.errorHandler = (err, instance, info) => {
    ErrorService.onError(err, info);
};

app.use(router).component('font-awesome-icon', FontAwesomeIcon).mount('#app');

app.use(PrimeVue);

// trigger/junk commit
