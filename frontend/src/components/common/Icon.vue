<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
import type { PropType } from 'vue';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    size: {
        type: String as PropType<IconSize>,
        required: false,
        default: IconSize.small,
    },
    class: {
        type: String,
        required: false,
    },
});

const icons = {
    // whenever we add an import here, we need to declare the module in alltypes.d.ts
    // to get rid of the type error
    // small icons
    close16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/close/16')
    ),
    'user--follow16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/user--follow/16')
    ),
    dashboard16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/dashboard/16')
    ),
    'virtual-column--key16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/virtual-column--key/16')
    ),
    settings16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/settings/16')
    ),
    help16: defineAsyncComponent(() => import('@carbon/icons-vue/es/help/16')),
    search16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/search/16')
    ),
    'checkmark--filled16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark--filled/16')
    ),
    checkmark16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark/16')
    ),
    'error--filled16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/error--filled/16')
    ),
    add16: defineAsyncComponent(() => import('@carbon/icons-vue/es/add/16')),
    'trash-can16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/trash-can/16')
    ),
    edit16: defineAsyncComponent(() => import('@carbon/icons-vue/es/edit/16')),
    'checkmark--outline16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark--outline/16')
    ),
    incomplete16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/incomplete/16')
    ),
    circleDash16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/circle-dash/16')
    ),
    warning16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/warning/16')
    'search--locate16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/search--locate/16')
    ),
    'group--access16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/group--access/16')
    ),

    // medium icons
    'checkmark--filled20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark--filled/20')
    ),
    checkmark: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark/20')
    ),
    'error--filled20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/error--filled/20')
    ),
    'warning--filled20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/warning--filled/20')
    ),
    login20: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/login/20')
    ),
    add20: defineAsyncComponent(() => import('@carbon/icons-vue/es/add/20')),
    'user--avatar--filled20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/user--avatar--filled/20')
    ),
    'user--avatar20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/user--avatar/20')
    ),
    'search--locate20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/search--locate/20')
    ),

    // large icons
    'error--filled24': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/error--filled/24')
    ),
    menu20: defineAsyncComponent(() => import('@carbon/icons-vue/es/menu/20')),
} as any;
</script>

<template>
    <component :is="icons[props.icon + props.size]" :class="class"></component>
</template>

<style lang="scss">
@import '@/assets/styles/icon.scss';
</style>
