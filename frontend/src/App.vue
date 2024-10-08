<script setup lang="ts">
import { defineAsyncComponent, shallowRef, watch, type Component } from "vue";
import { useRoute } from "vue-router";
import AuthProvider from "@/providers/AuthProvider.vue";
import { VueQueryDevtools } from "@tanstack/vue-query-devtools";

const route = useRoute();
const layout_component = shallowRef<Component>();

watch(
    () => route.meta.layout ?? "SimpleLayout",
    (layout) => {
        layout_component.value = defineAsyncComponent(
            () => import(`@/layouts/${layout}.vue`)
        );
    },
    { immediate: true }
);
</script>

<template>
    <AuthProvider>
        <component :is="layout_component">
            <router-view />
        </component>
        <VueQueryDevtools />
    </AuthProvider>
</template>

<style lang="scss">
@import "primeflex/primeflex.css";
@import "@/assets/styles/styles.scss";
@import "primevue/resources/primevue.min.css";
@import "primevue/resources/themes/bootstrap4-light-blue/theme.css";
</style>
