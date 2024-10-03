<script setup lang="ts">
import { hashRouter } from '@/router';
import { useRoute } from 'vue-router';

console.warn(`Route "${useRoute().path}" not found, redirect to home.`);
hashRouter.push('/');
</script>

<template></template>
