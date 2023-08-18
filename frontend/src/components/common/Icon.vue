<script setup lang="ts">
import { computed, defineAsyncComponent, type PropType } from 'vue';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    size: {
        type: String as PropType<IconSize>,
        required: true,
        default: IconSize.small,
    },
    class: {
        type: String,
        required: true,
    }
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
        :class="class"
    ></component>
</template>

<style lang="scss">
@import '@/assets/styles/icon.scss';
</style>
