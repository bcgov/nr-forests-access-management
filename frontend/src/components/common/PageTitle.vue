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
    <Breadcrumb
        v-if="route.meta.hasBreadcrumb"
        :model="breadcrumbState"
        :pt="{
            menuitem: { class: 'custom-menuitem' },
        }"
    >
        <template #item="{ item }">
            <RouterLink
                v-if="item.path"
                :to="item.path"
                class="custom-menuitem-link"
            >
                <span class="custom-menutitem-text">{{ item.label }}</span>
            </RouterLink>
        </template>
    </Breadcrumb>
    <h1 class="title">{{ props.title }}</h1>
    <h2 class="subtitle">{{ props.subtitle }}</h2>
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
}

.custom-menuitem:focus-visible,
.custom-menuitem-link:focus-visible {
    outline: none;
}

.custom-menuitem-link {
    padding: 0.2rem;
    text-decoration: none;
}

.custom-menuitem-link:focus {
    box-shadow: inset 0 0px 0px 0.063rem $light-focus;
}

.custom-menuitem:last-child .custom-menuitem-link {
    pointer-events: none;
}

.custom-menutitem-text {
    color: $light-link-primary;
}

.custom-menutitem-text:hover {
    color: $light-link-primary-hover;
}

.custom-menuitem:last-child .custom-menutitem-text {
    color: $light-text-primary;
    display: contents;
}
</style>
