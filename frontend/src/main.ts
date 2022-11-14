import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';

import './assets/styles/styles.scss'
import 'bootstrap'

Amplify.configure(awsExports); // Config Amplify for Cognito resource.

const app = createApp(App)

app.use(router)

app.mount('#app')
