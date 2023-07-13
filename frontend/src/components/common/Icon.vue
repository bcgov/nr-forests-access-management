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
    width: 32px;
    height: 32px;
}
.icon-medium {
    width: 20px;
    height: 20px;
}

.icon-small {
    width: 16px;
    height: 16px;
}
</style>
