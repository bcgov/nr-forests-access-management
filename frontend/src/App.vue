<script setup lang="ts">
import Breadcrumb from '@/components/Breadcrumb.vue';
import Footer from '@/components/footer/Footer.vue';
import Header from '@/components/header/Header.vue';
import { RouterView } from 'vue-router';

</script>

<template>
  <Header></Header>
  <main class="container pt-0 mt-2">
    <Breadcrumb />
    <RouterView />
    <modals-container></modals-container>
  </main>

  <Footer></Footer>

</template>

<style lang="scss" scoped>
  @import "~bootstrap/scss/bootstrap";

</style>
