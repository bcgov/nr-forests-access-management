<script setup lang="ts">
import router from '@/router';
import { useRoute } from 'vue-router';
import { useToastService } from '@/store/ToastState';

const notFoundMsg = `Route "${useRoute().path}" not found, redirect to home.`;
console.log(notFoundMsg);
const { showToastErrorTopRight } = useToastService();
showToastErrorTopRight(notFoundMsg);
router.push('/');
</script>

<template></template>
