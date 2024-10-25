<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AuthProvider from "@/providers/AuthProvider.vue";
import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import ProtectedLayout from "@/layouts/ProtectedLayout.vue";

// Get the current route
const route = useRoute();

// Use computed to determine which layout to use
const layoutComponent = computed(() => {
    return route.meta.layout === "ProtectedLayout" ? ProtectedLayout : null;
});
</script>

<template>
    <AuthProvider>
        <!-- Render the layout if provided, otherwise just the router-view -->
        <component v-if="layoutComponent" :is="layoutComponent" />
        <!-- No layout, just render the view -->
        <router-view v-else />
        <VueQueryDevtools />
    </AuthProvider>
</template>

<style lang="scss">
@import "primeflex/primeflex.css";
@import "@/assets/styles/styles.scss";
@import "@/assets/styles/themes.scss";
@import "primevue/resources/primevue.min.css";
@import "primevue/resources/themes/bootstrap4-light-blue/theme.css";
</style>
