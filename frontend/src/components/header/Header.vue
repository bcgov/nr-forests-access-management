<script setup lang="ts">
  import { inject } from 'vue';

  let environmentLabel = inject('fam_environment_display_name') as string
  console.log("environmentLabel: ", environmentLabel)
  if (environmentLabel && environmentLabel.length > 0) {
    environmentLabel = ` (${environmentLabel.toUpperCase()})`
  }

</script>

<template>

  <header class="container-fluid app-header" id="header">
    <nav class="navbar navbar-expand-md justify-content-between px-2">
      <a class="navbar-brand" title="Forest Access Management" href="https://www2.gov.bc.ca" style="margin-right: 0;">
        <img
            class="nav-logo img-fluid d-none d-sm-block"
            src="@/assets/images/17_gov3_bc_logo.svg"
            width="152" height="55"
            alt="B.C. Government Logo">
      </a>
      <!-- <img alt="BC Gov logo" class="logo" src="@/assets/bcgov-header-horiz-LG.png" width="140" height="60" /> -->
      <h2>Forest Access Management {{environmentLabel}}</h2>
      
      <button class="navbar-toggler" type="button" title="Toggle Main Navigation"
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
        data-toggle="collapse"
        data-target="#navbarNav">
        <em class="material-icons">menu</em>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" title="Log In">
              <span>Log In</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" title="Contact Us">
              <span>Contact Us</span>
            </a>
          </li>
        </ul>
      </div>
    </nav>
  
    <nav class="bc-nav-links navbar-expand-md py-0">
      <div class="collapse navbar-collapse" id="menuLink">
        <ul class="navbar-nav">
          <li class="nav-item" @click="$router.push({ name: 'about'})">
            <a class="nav-link" title="About">
              <span>About</span>
            </a>
          </li>
          <li class="nav-item" @click="$router.push({ name: 'home' })">
            <a class="nav-link" title="Home">
              <span>Home</span>
            </a>
          </li>
          <li class="nav-item" @click="$router.push({ name: 'application' })">
            <a class="nav-link" title="Select Application">
              <span>Select Application</span>
            </a>
          </li>
        </ul>

      </div>
    </nav>
  </header>

</template>

<style lang="scss" scoped>
  @import "./header.scss";
</style>
