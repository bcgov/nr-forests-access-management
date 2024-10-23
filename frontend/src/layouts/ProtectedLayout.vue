<script setup lang="ts">
import Header from "@/components/UI/Header.vue";
import SideNav from "@/components/UI/SideNav.vue";
</script>

<template>
    <div>
        <!-- Show layout and content -->
        <Header title="FAM" subtitle="Forests Access Management" />
        <SideNav />
        <div class="main">
            <main>
                <router-view />
                <!-- Render protected routes here -->
            </main>
        </div>
    </div>
</template>
