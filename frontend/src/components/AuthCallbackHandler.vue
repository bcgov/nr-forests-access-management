<script setup lang="ts">
import router from '@/router';
import authService from '@/services/AuthService';
import { getNavigationPath } from '@/store/NavigationState';

/**
 * This component is to deal with Auth callback.
 */

authService.methods.handlePostLogin().then((data) => {
    const navigationPath = getNavigationPath();
    if (navigationPath) {
        router.push(navigationPath);
    } else {
        router.push('/dashboard');
    }
});
</script>

<template></template>
