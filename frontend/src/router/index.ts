import { defineComponent } from "vue";
import {
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from "vue-router";
import { routeItems } from "@/router/RouteItem";
import { authGuard, landingGuard } from "@/router/RouteGuards";

// Define the component for the auth callback (an empty div)
const AuthCallbackComponent = defineComponent({
    template: "<div></div>",
});

// Hash-based router for the main app routes
const hashRouter = createRouter({
    history: createWebHashHistory(),
    routes: routeItems.map((route) => {
        if (route.name === "Landing") {
            return { ...route, beforeEnter: landingGuard }; // Apply landing guard
        } else {
            return { ...route, beforeEnter: authGuard }; // Apply auth guard to all other routes
        }
    }),
});

// History-based router for the auth callback
const historyRouter = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/authCallback",
            name: "AuthCallback",
            component: AuthCallbackComponent, // Using defineComponent for an empty div
        },
    ],
});

export { hashRouter, historyRouter };
