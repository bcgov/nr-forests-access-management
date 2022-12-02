import { createApp } from 'vue'

import Toast, { useToast, POSITION, TYPE } from "vue-toastification";
// Import the CSS or use your own!
import "vue-toastification/dist/index.css";

import App from '@/App.vue'
import router from '@/router'
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';

import './assets/styles/styles.scss'
import 'bootstrap'

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App)

app.use(Toast, {
    // // Defaults for all toast messages
    // position: POSITION.TOP_RIGHT,
    // timeout: 5000, // milliseconds
    newestOnTop: true,

    // Prevent having multiple messages with the same type and content from being displayed.
    filterBeforeCreate: (toast, toasts) => {
      if (toasts.filter(t => t.type === toast.type && t.content === toast.content).length !== 0) {
        // Returning false discards the toast
        return false;
      }
      return toast;
    },

    toastDefaults: {
        // ToastOptions object for each type of toast
        [TYPE.ERROR]: {
            position: POSITION.TOP_CENTER,
            timeout: false,
        },
        [TYPE.SUCCESS]: {
            position: POSITION.TOP_RIGHT,
            timeout: 4000,
            hideProgressBar: true,
        }
    }
});

app.config.errorHandler = (err, instance, info) => {
    // If triggered on component setup/initial render, this can display many times.
    // This can trigger on an uncaught error in a function.
    // This will NOT trigger on an uncaught error in an async setup operation.
    const toast = useToast();
    toast.error("An application error has occurred. Please try again. If the error persists contact support.")
    console.log(`app.config.errorHandler error ${err} with info: ${info}`)
}

app.use(router)

app.mount('#app')
