<script setup lang="ts">
import router from '@/router';
import authService from '@/services/AuthService';

/**
 * This component is to deal with Auth callback.
 */

authService.handlePostLogin().then((data) => {
    router.push('/dashboard');
});
</script>

<template></template>
