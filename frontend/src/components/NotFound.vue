<script setup lang="ts">
import { router } from "@/router";
import { useRoute } from "vue-router";

console.warn(`Route "${useRoute().path}" not found, redirect to home.`);
router.push("/");
</script>

<template></template>
