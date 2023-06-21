<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import sidebarData from '@/static/sidebar.json';
</script>
<template>
    <Header />
    <Sidebar :data="sidebarData" />
    <div class="container">
        <main>
            <!-- <Breadcrumb /> -->
            <RouterView></RouterView>
            <modals-container></modals-container>
        </main>
    </div>
</template>
<style lang="scss">
@import '@/assets/styles/default-theme.scss';
</style>
