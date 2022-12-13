import { createApp } from 'vue'

import Toast, { useToast, type PluginOptions, POSITION, TYPE } from "vue-toastification"
import "vue-toastification/dist/index.css"

import { Amplify } from 'aws-amplify'
import awsExports from './aws-exports'
import { PromiseDialog } from 'vue3-promise-dialog'

import App from '@/App.vue'
import router from '@/router'

import './assets/styles/styles.scss'
import 'bootstrap'

// import the fontawesome core
import { library } from '@fortawesome/fontawesome-svg-core'

// import font awesome icon component
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// import specific icons
import { faTrashCan } from '@fortawesome/free-regular-svg-icons'

// add specific icons to library for use throughout application
library.add(faTrashCan)

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App)

const toastOptions: PluginOptions = {
  // // Defaults for all toast messages
  position: POSITION.TOP_RIGHT,
  timeout: 5000, // milliseconds
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
      }
  }
}


app.use(Toast, );

app.config.errorHandler = (err, instance, info) => {
    // This can trigger on an uncaught error in a function.
    // This will NOT trigger on an uncaught error in an async setup operation.
    const toast = useToast();
    toast.error("An application error has occurred. Please try again. If the error persists contact support.")
    console.log(`app.config.errorHandler error ${err} with info: ${info}`)
}

app
  .use(router)
  .use(PromiseDialog)
  .component('font-awesome-icon', FontAwesomeIcon)
  .mount('#app')
