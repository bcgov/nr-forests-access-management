<script setup lang="ts">
import router from '@/router';
import { useRoute } from 'vue-router';
import { showToastErrorTopRight } from '@/store/ToastState';

const notFoundMsg = `Route "${useRoute().path}" not found, redirect to home.`;
console.log(notFoundMsg);
showToastErrorTopRight(notFoundMsg);
router.push('/');
</script>

<template></template>
