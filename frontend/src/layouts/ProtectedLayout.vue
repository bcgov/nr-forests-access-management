<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import Footer from '@/components/footer/Footer.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
</script>
<template>
    <Header></Header>
    <main class="container">
        <Breadcrumb />
        <RouterView />
        <modals-container></modals-container>
    </main>
    <Footer></Footer>
</template>
