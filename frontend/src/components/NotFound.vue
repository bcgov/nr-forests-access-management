<script setup lang="ts">
    import router from '@/router';
    import { useRoute } from 'vue-router';

    console.log(`Route "${useRoute().path}" not found, redirect to home.`)
    router.push("/")
</script>

<template>

</template>
