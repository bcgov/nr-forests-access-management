<script setup>
import Button from 'primevue/button';
const props = defineProps({
    label: {
        type: String,
        default: 'Click',
    },
});
</script>
<template>
    <Button class="nr-button"
        ><span>{{ props.label }}</span> <slot class="icon"></slot
    ></Button>
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
