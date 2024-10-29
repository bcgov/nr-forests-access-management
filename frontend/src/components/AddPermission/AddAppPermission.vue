<script setup lang="ts">
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

// Access the path parameters
const userId = route.params.userId as string | undefined;
const applicationId = route.params.applicationId as string | undefined;

// if (!userId || !applicationId) {
//     console.warn("Missing required path params");
//     router.push("/");
// }

const navigateBack = () => {
    router.push("/");
};

// Breadcrumb configuration
const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
    },
];
</script>

<template>
    <BreadCrumbs :crumbs="crumbs" />
</template>
<style lang="scss"></style>
