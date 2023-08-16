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

<style lang="scss">
.icon-large {
    width: 2rem !important;
    height: 2rem !important;
}
.icon-medium {
    width: 1.25rem !important;
    height: 1.25rem !important;
}

.icon-small {
    width: 1rem !important;
    height: 1rem !important;
}
</style>
