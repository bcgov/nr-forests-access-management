<script setup lang="ts">
import { inject } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const environmentDisplayName = inject('fam_environment_display_name') as string
var environmentLabel = ''
if (environmentDisplayName.length > 0) {
  environmentLabel = ` (${environmentDisplayName.toUpperCase()})`
}
</script>

<template>
  <header>
    <img alt="BC Gov logo" class="logo" src="@/assets/bcgov-header-horiz-LG.png" width="140" height="60" />

    <div class="wrapper">
      <h1>FAM - Forest Access Management {{environmentLabel}}</h1>
      
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/application">Select Application</RouterLink>
        <!-- <RouterLink to="/manage">Manage Access</RouterLink> -->
        <RouterLink to="/about">About</RouterLink>

      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>

  <Footer></Footer>

</template>

<style lang="scss" scoped>
  @import "~bootstrap/scss/bootstrap";

</style>
