<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import sideNavData from '@/static/sideNav.json';
import SideNav from '@/components/common/SideNav.vue';
</script>
<template>
    <Header title="FAM" subtitle="Forest Access Management" />

    <SideNav :data="(sideNavData as any)" />
    <div class="main">
        <main>
            <RouterView></RouterView>
        </main>
    </div>
</template>
<style lang="scss">
@import '@/assets/styles/base.scss';
</style>
