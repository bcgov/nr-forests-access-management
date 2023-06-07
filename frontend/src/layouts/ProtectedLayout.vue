<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import Footer from '@/components/footer/Footer.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
</script>
<template>
    <Header></Header>

    <Sidebar />

    <div class="main">
        <main class="container">
            <!-- <Breadcrumb /> -->
            <RouterView />
            <modals-container></modals-container>
        </main>
    </div>
    <!-- <Footer></Footer> -->
</template>
<style>
.main {
    position: absolute;
    display: block;
    top: 48px;
    left: 256px;
}
</style>
