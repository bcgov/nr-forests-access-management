<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router';
import Breadcrumb from 'primevue/breadcrumb';
import { breadcrumbState } from '@/store/BreadcrumbState';

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: true,
    },
});

const route = useRoute();
</script>

<template>
    <Breadcrumb v-if="route.meta.hasBreadcrumb" :model="breadcrumbState">
        <template #item="{ item }">
            <RouterLink v-if="item.path" :to="item.path">
                <span>
                    {{ item.label }}
                </span>
            </RouterLink>
        </template>
    </Breadcrumb>
    <h1 class="title">{{ props.title }}</h1>
    <p class="subtitle" aria-roledescription="subtitle">
        {{ props.subtitle }}
    </p>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
.title {
    font-size: 2rem;
    line-height: 2.5rem;
    color: $light-text-primary;
    font-weight: 400;
}

.subtitle {
    font-size: 0.875rem;
    line-height: 1.125rem;
    letter-spacing: 0.01rem;
    color: $light-text-secondary;
    margin-bottom: 0.5rem;
}
</style>
