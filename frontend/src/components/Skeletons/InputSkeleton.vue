<script setup lang="ts">
import Skeleton from "primevue/skeleton";
defineProps<{
    width?: string;
    height?: string;
}>();
</script>
<template>
    <Skeleton
        class="fam-input-skeleton"
        :height="height ?? '2.5rem'"
        :width="width ?? '38rem'"
    />
</template>
