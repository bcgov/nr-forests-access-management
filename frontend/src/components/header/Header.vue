<script setup lang="ts">
  import { EnvironmentSettings } from '@/services/EnvironmentSettings';
  import authService from '@/services/AuthService';

  const environmentSettings = new EnvironmentSettings()
  const environmentLabel = environmentSettings.getEnvironmentDisplayName("[","]").toUpperCase()

</script>

<template>

  <header class="app-header" id="header">
    <nav class="navbar navbar-expand-md justify-content-between px-2 navbar-dark">
      <a class="navbar-brand" title="Forest Access Management" href="https://www2.gov.bc.ca" style="margin-right: 3px;">
        <img
            class="nav-logo"
            src="@/assets/images/17_gov3_bc_logo.svg"
            alt="B.C. Government Logo">
      </a>

      <h2 class="title">Forest Access Management {{environmentLabel}}</h2>
      
      <button class="navbar-toggler" type="button" 
        title="Toggle Main Navigation"
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link nav-link-fade-up" title="Log In"
              v-if="!authService.state.famUser"
              @click="authService.methods.login">
              <span>Log In</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link nav-link-fade-up" title="Log In"
              v-if="authService.state.famUser"
              @click="authService.methods.logout">
              <span>Log Out</span>
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

    <div class="nav bc-nav">
        <a class="nav-link" title="About" 
          @click="$router.push({ name: 'about'})">
          <span>About</span>
        </a>
        <a class="nav-link" title="Home" 
          @click="$router.push({ name: 'home' })">
          <span>Home</span>
        </a>
        <a class="nav-link" title="Select Application" 
          @click="$router.push({ name: 'application' })">
          <span>Select Application</span>
        </a>
    </div>
  </header>

</template>

<style lang="scss" scoped>
  @import "./header.scss";
</style>
