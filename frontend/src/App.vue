<script setup lang="ts">

  import { RouterView } from 'vue-router'
  import Header from '@/components/header/Header.vue'
  import Footer from '@/components/footer/Footer.vue'
  import Breadcrumb from '@/components/Breadcrumb.vue'

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
