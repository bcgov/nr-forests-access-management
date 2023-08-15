<script setup lang="ts">
import { computed, defineAsyncComponent, type PropType } from 'vue';

enum IconSize {
    small = '16',
    medium = '20',
    large = '24',
    xLarge = '32'
}

const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    size: {
        type: String as PropType<IconSize>,
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
