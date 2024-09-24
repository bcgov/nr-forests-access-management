<script setup lang="ts">
import { defineAsyncComponent, shallowRef, watch, type Component } from 'vue';
import { RouterView } from 'vue-router';
import { useRoute } from 'vue-router';
import ToastMessage from '@/components/common/ToastMessage.vue';
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'

const route = useRoute();
const layout_component = shallowRef<Component>();
watch(
    () => route.meta.layout ?? 'SimpleLayout',
    (layout) => {
        layout_component.value = defineAsyncComponent(
            () => import(`@/layouts/${layout}.vue`)
        );
    },
    { immediate: true }
);
</script>

<template>
    <ToastMessage />
    <component :is="layout_component">
        <router-view />
    </component>
    <VueQueryDevtools />
</template>

<style lang="scss">
@import 'primeflex/primeflex.css';
@import '~bootstrap/scss/bootstrap';
@import '@/assets/styles/styles.scss';
@import 'primevue/resources/primevue.min.css';
@import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
</style>
