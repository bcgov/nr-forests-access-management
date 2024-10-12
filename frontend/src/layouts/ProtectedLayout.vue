<script setup lang="ts">
import { ref } from "vue";
import type { ISideNavItem } from "@/components/common/SideNav.vue";
import Header from "@/components/header/Header.vue";
import SideNav from "@/components/common/SideNav.vue";
import sideNavData from "@/static/sideNav.json";

const navigationData = ref<[ISideNavItem]>(sideNavData as any);
</script>

<template>
    <div>
        <!-- Show layout and content -->
        <Header title="FAM" subtitle="Forests Access Management" />
        <SideNav :data="navigationData" />
        <div class="main">
            <main>
                <RouterView />
                <!-- Render protected routes here -->
            </main>
        </div>
    </div>
</template>
