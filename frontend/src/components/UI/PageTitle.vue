<script setup lang="ts">
import { useRoute } from "vue-router";

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: false,
    },
});

const route = useRoute();
</script>

<template>
    <div>
        <h5 class="title">{{ props.title }}</h5>
        <p
            v-if="props.subtitle"
            class="subtitle"
            aria-roledescription="subtitle"
        >
            {{ props.subtitle }}
        </p>
    </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/base.scss";

.title {
    @include type.type-style("heading-05");
    color: var(--text-primary);
}

.subtitle {
    @include type.type-style("body-01");
    color: var(--text-secondary);
}
</style>
