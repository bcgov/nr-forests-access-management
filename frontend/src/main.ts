import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'

import './assets/styles/styles.scss'
import 'bootstrap'

const app = createApp(App)

const apiBaseUrl = window.localStorage.getItem('fam_api_base_url') as string;
console.log(`FAM API Base URL ${apiBaseUrl}`)
app.provide('fam_api_base_url', apiBaseUrl)

const environmentDisplayName = window.localStorage.getItem('environment_display_name') as string;
console.log(`Environment ${environmentDisplayName}`)
app.provide('fam_environment_display_name', environmentDisplayName)

app.use(router)

app.mount('#app')
