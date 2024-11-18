import { createRouter, createWebHashHistory } from "vue-router";
import { routeItems } from "@/router/routes";
import { authGuard, landingGuard } from "@/router/RouteGuards";

// Hash-based router for the main app routes
export const router = createRouter({
    history: createWebHashHistory(),
    routes: routeItems.map((route) => {
        if (route.name === "Landing") {
            return { ...route, beforeEnter: landingGuard }; // Apply landing guard
        } else {
            return { ...route, beforeEnter: authGuard }; // Apply auth guard to all other routes
        }
    }),
    scrollBehavior(to) {
        // Check if the route has the `protectedLayoutMeta`
        if (to.meta?.layout === "ProtectedLayout") {
            return {
                top: 0,
                behavior: "smooth",
                el: "#proctected-layout-container",
            };
        }
        // Default behavior (no scrolling for other routes)
        return false;
    },
});
