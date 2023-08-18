<script setup lang="ts">
const props = defineProps({
    text: {
        type: String,
        required: true,
        default: '',
    },
    active: {
        type: Boolean,
        required: true,
        default: false,
    },
});
</script>
<template>
    <div
        class="tag"
        :class="{ 'tag--success': props.active, 'tag--error': !props.active }"
    >
        {{ props.text }}
    </div>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.tag {
    font-size: .75rem;
    letter-spacing: .02rem;
    display: flex;
    width: fit-content;
    padding-left: .625rem;
    padding-right: .625rem;
    height: 1.5rem;
    align-items: center;
    border-radius: 62.5rem;
}

.tag--error {
    background: #ffe5f2;
    color: #800241;
}

.tag--success {
    background: #cce5cc;
    color: #005500;
}
</style>
