<script setup lang="ts">
import Button from 'primevue/button';
import { ref, type PropType, watchEffect } from 'vue';
import { IconPosition } from '@/enum/IconEnum';
import LoadingState from '@/store/LoadingState';

const props = defineProps({
    label: {
        type: String,
        default: 'Click',
    },
    loadingLabel: {
        type: String,
        default: 'Loading...',
    },
    iconPosition: {
        type: String as PropType<IconPosition>,
        default: IconPosition.right,
    },
    // Give a name if the parent component has more than 1 button
    // and need to identify which button being clicked.
    name: {
        type: String,
        default: '',
    },
});

const tLabel = ref(props.label); // for this template dynamic labeling.
let targetButtonClicked = false; // target button.
watchEffect(() => {
    if (targetButtonClicked && LoadingState.isLoading.value) {
        tLabel.value = props.loadingLabel;
    }

    // reset when loading is done.
    if (!LoadingState.isLoading.value) {
        targetButtonClicked = false;
        tLabel.value = props.label;
    }
});

function onClicked(event: any) {
    // determine this is the target button being clicked.
    if (event['target']['name'] == props.name) {
        targetButtonClicked = true;
    }
}
</script>
<template>
    <Button class="nr-button" :name="props.name" @click="onClicked($event)">
        <slot
            class="icon"
            v-if="props.iconPosition === IconPosition.left"
        ></slot>
        <span>{{ tLabel }}</span>
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
