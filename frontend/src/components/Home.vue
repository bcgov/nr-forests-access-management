<script setup lang="ts">
import authService from '@/services/AuthService';
</script>

<template>
    <h1>Welcome to FAM</h1>
    <br />
    <h2 v-if="!authService.getters.isLoggedIn()">Please Sign In</h2>
</template>
