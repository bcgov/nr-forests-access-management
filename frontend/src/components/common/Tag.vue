<template>
    <div class="tag" :class="{ 'tag--success': active, 'tag--error': !active }">
        {{ text }}
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const selected = ref('');
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

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.tag {
    /* Auto layout */
    /* Inside auto layout */
    flex: none;
    order: 0;
    flex-grow: 0;

    // width: 36px;
    // height: 16px;

    /* Utility styles/label-01 */
    // font-family: 'BC Sans';
    font-style: normal;
    font-weight: 400;
    font-size: 12px;
    line-height: 16px;
    /* identical to box height, or 133% */
    letter-spacing: 0.32px;

    display: flex;
    flex-direction: row;
    align-items: flex-start;
    padding: 0px;

    width: fit-content;
    padding-left: 10px;
    padding-right: 10px;
    height: 24px;
    align-items: center;
    justify-content: center;
    margin-bottom: 21px;

    /* Light Theme/Tag/Cyan background */

    border-radius: 1000px;

    /* Inside auto layout */
    flex: none;
    order: 0;
    flex-grow: 0;
}

.tag--error {
    /* Light Theme/Tag/Pink background */
    background: #ffe5f2;
    color: #800241;
}

.tag--success {
    background: #cce5cc;
    color: #005500;
}
</style>
