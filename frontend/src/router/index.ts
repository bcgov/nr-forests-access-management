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
        if (to.meta?.layout === "ProtectedLayout") {
            const mainElement = document.querySelector(".main");
            if (mainElement) {
                mainElement.scrollTo({
                    top: 0,
                    behavior: "smooth",
                });
            }
            return false; // Prevent default Vue Router scrolling behavior
        }
        return false; // Default behavior for other routes
    },
});
