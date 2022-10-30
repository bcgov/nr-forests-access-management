<script lang="ts">

  import { RouterView } from 'vue-router'
  import Header from '@/components/header/Header.vue'
  import Footer from '@/components/footer/Footer.vue'

  export default {
    components: {
      FamHeader: Header,
      FamFooter: Footer
    }
  }

</script>

<template>
  <FamHeader />

  <main class="container pt-0 mt-2">
    <RouterView />
  </main>

  <FamFooter />

</template>

<style lang="scss" scoped>
  @import "~bootstrap/scss/bootstrap";

</style>
