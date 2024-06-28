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
        required: true,
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
    misuse16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/misuse/16')
    ),
    add16: defineAsyncComponent(() => import('@carbon/icons-vue/es/add/16')),
    'trash-can16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/trash-can/16')
    ),
    edit16: defineAsyncComponent(() => import('@carbon/icons-vue/es/edit/16')),
    'search--locate16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/search--locate/16')
    ),
    'group--access16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/group--access/16')
    ),
    user16: defineAsyncComponent(() => import('@carbon/icons-vue/es/user/16')),
    enterprise16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/enterprise/16')
    ),
    'user--profile16': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/user--profile/16')
    ),
    document16: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/document/16')
    ),

    // medium icons
    'checkmark--filled20': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark--filled/20')
    ),
    checkmark: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/checkmark/20')
    ),
    misuse20: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/misuse/20')
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
    misuse24: defineAsyncComponent(
        () => import('@carbon/icons-vue/es/misuse/24')
    ),
    menu20: defineAsyncComponent(() => import('@carbon/icons-vue/es/menu/20')),

    // xlarge
    'search--locate32': defineAsyncComponent(
        () => import('@carbon/icons-vue/es/search--locate/32')
    ),
} as any;
</script>

<template>
    <component :is="icons[props.icon + props.size]" :class="class"></component>
</template>

<style lang="scss">
@import '@/assets/styles/icon.scss';
</style>
