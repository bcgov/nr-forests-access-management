<script lang="ts" setup>
import { RouterLink } from "vue-router";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";

defineProps<{
    crumbs: BreadCrumbType[];
}>();
</script>

<template>
    <div class="breadcrumbs-container">
        <template v-for="crumb in crumbs">
            <RouterLink class="crumb-label" :to="{ name: crumb.routeName }">
                <span>
                    {{ crumb.label }}
                </span>
            </RouterLink>
            <span class="separator">/</span>
        </template>
    </div>
</template>

<style lang="scss">
.breadcrumbs-container {
    margin-bottom: 0.5rem;
    .crumb-label {
        text-decoration: none;
        color: colors.$blue-70;
    }

    .separator {
        margin: 0 0.5rem;
    }
}
</style>
