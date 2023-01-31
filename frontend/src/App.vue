<script setup lang="ts">

import awsExports from '@/aws-exports';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Footer from '@/components/footer/Footer.vue';
import Header from '@/components/header/Header.vue';
import { Amplify } from 'aws-amplify';
import { RouterView } from 'vue-router';

Amplify.configure(awsExports); // Config Amplify for Cognito resource.
  
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
