<script setup lang="ts">

  import { RouterView } from 'vue-router'
  import Header from '@/components/header/Header.vue'
  import Footer from '@/components/footer/Footer.vue'

</script>

<template>
  <Header></Header>

  <main class="container pt-0 mt-2">
    <RouterView />
  </main>

  <Footer></Footer>

</template>

<style lang="scss" scoped>
  @import "~bootstrap/scss/bootstrap";

</style>
