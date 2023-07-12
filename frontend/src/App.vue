<script setup lang="ts">
import { RouterView } from 'vue-router';
import { defineAsyncComponent, shallowRef, watch, type Component } from 'vue';
import { useRoute } from 'vue-router';

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
    <component :is="layout_component">     
        <router-view />
    </component>
</template>

<style lang="scss">
@import '~bootstrap/scss/bootstrap';
</style>
