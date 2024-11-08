<script setup lang="ts">
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import { useRouter } from "vue-router";
import PageTitle from "@/components/common/PageTitle.vue";

const router = useRouter();

// Breadcrumb configuration
const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
    },
];
</script>

<template>
    <div class="add-fam-permission-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            title="Add application admin"
            subtitle="All fields are mandatory"
        />
    </div>
</template>
<style lang="scss">
.add-fam-permission-container {
}
</style>
