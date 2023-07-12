<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import sidebarData from '@/static/sidebar.json';
import ToastMessage from '@/components/common/ToastMessage.vue';
</script>
<template>
    <Header />
    <ToastMessage />
    <Sidebar :data="sidebarData" />
    <div class="main">
        <main>
            <!-- <Breadcrumb /> -->
            <RouterView></RouterView>
            <modals-container></modals-container>
        </main>
    </div>
</template>
<style lang="scss">
@import '@/assets/styles/base.scss';
</style>
