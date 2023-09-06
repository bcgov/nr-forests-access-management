<script setup lang="ts">
import Button from 'primevue/button';
import type { PropType } from 'vue';
import { IconPosition } from '@/enum/IconEnum';

const props = defineProps({
    label: {
        type: String,
        default: 'Click',
    },
    iconPosition: {
        type: String as PropType<IconPosition>,
        default: IconPosition.right,
    },
});
</script>
<template>
    <Button class="nr-button">
        <slot
            class="icon"
            v-if="props.iconPosition === IconPosition.left"
        ></slot>
        <span>{{ props.label }}</span>
        <slot
            class="icon"
            v-if="props.iconPosition === IconPosition.right"
        ></slot>
    </Button>
</template>
<style lang="scss">
.nr-button {
    display: flex;
}
.nr-button .icon {
    margin-right: auto;
}

.nr-button span {
    margin-right: auto;
}
</style>
