<template>
    <component
        :class="{
            'icon-small': small,
            'icon-medium': medium,
            'icon-large': large,
        }"
        :is="iconName"
    ></component>
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue';
const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    small: {
        type: Boolean,
        required: false,
        default: false,
    },
    medium: {
        type: Boolean,
        required: false,
        default: false,
    },
    large: {
        type: Boolean,
        required: false,
        default: false,
    },
});
const iconName = computed(() => {
    return defineAsyncComponent(() => import(`../icons/${props.icon}.vue`));
});
</script>

<style lang="scss">
.icon-large {
    width: 32px !important;
    height: 32px !important;
}
.icon-medium {
    width: 20px !important;
    height: 20px !important;
}

.icon-small {
    width: 16px !important;
    height: 16px !important;
}
</style>
