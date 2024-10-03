<script setup lang="ts">
import authService from '@/services/AuthService';

/**
 * This component is to deal with Auth callback.
 */

authService.handlePostLogin().then(() => {
    window.location.href = '/#/dashboard';
});
</script>

<template></template>
