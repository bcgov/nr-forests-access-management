<script setup lang="ts">
import { useRoute } from 'vue-router';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';

const props = defineProps<{
    displaySelectedApplication?: boolean;
}>();
</script>

<template>
    <div class="title" v-if="props.displaySelectedApplication">
        {{ selectedApplicationDisplayText }}
    </div>

    <hr class="hr-text" :data-content="useRoute().meta.title" />
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.title {
    margin-top: 0.2rem;
    font-weight: 600;
    line-height: 1.1;
    font-size: calc(1.3324rem + 0.9888vw);
    @include media-breakpoint-down(sm) {
        font-size: 1.35rem;
    }
}

.hr-text {
    line-height: 1em;
    position: relative;
    outline: 0;
    border: 0;
    color: black;
    text-align: center;
    height: 1.8em;
    opacity: 0.7;
    &:before {
        content: '';
        // use the linear-gradient for the fading effect
        // use a solid background color for a solid bar
        background: linear-gradient(
            to right,
            transparent,
            #818078,
            transparent
        );
        position: absolute;
        left: 0;
        top: 50%;
        width: 100%;
        height: 1px;
    }
    &:after {
        content: attr(data-content);
        position: relative;
        display: inline-block;
        color: black;
        padding: 0 0.5em;
        line-height: 1em;
        // this is really the only tricky part, you need to specify the background color of the container element...
        background-color: #fcfcfa;
        font-size: 1.5rem;
        font-weight: 600;
    }
}
</style>
