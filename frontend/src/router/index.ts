import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ManageAccessView from '../views/ManageAccessView.vue'

import ApplicationSelection from '../components/ApplicationSelection.vue'
// import ManageAccess from '../components/ManageAccess.vue'
import GrantAccess from '../components/GrantAccess.vue'

// WARNING: any components referenced below that themselves reference the router cannot be automatically hot-reloaded in local development due to circular dependency
// See vitejs issue https://github.com/vitejs/vite/issues/3033 for discussion.
// Symptoms: you will see the following errors in your browser's Javascript console: 
// ReferenceError: Cannot access 'ApplicationSelection' before initialization at index.ts:21:18
// Failed to reload /src/components/ApplicationSelection.vue. This could be due to syntax errors or importing non-existent modules.
// Workaround: reload the page in the browser
// Workarounds:
// 1. Reload the page in the browser if the hot-reload fails.
// 2. (Not recommended) Within router below, use the component: () => import(../components/<component>.vue) syntax. This fixes the issue, but seems to break using shared state (e.g. in ApplicationService).
// 3. Within router below use a wrapper view compoent. The component referenced by the wrapper can be hot-reloaded, while updates to the wrapper view would still trigger this issue.


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/application',
      name: 'application',
      component: ApplicationSelection // () => import('../components/ApplicationSelection.vue')
    },
    {
      path: '/manage',
      name: 'manage',
      component: ManageAccessView
    },
    {
      path: '/grant',
      name: 'grant',
      component: GrantAccess
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
