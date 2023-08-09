<script setup>
import { computed, defineAsyncComponent } from 'vue';
const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    size: {
        type: String,
        required: true,
        default: '16',
    },
});
const iconName = computed(() => {
    // dynamic imports must start with ./ or ../ and must end with a file extension
    // https://github.com/rollup/plugins/tree/master/packages/dynamic-import-vars#limitations
    return defineAsyncComponent(() => import(`../../../node_modules/@carbon/icons-vue/es/${props.icon}/${props.size}.js`));
});
</script>

<template>
    <component
        :is="iconName"
    ></component>
</template>
