<script setup lang="ts">
import { defineProps } from 'vue';

// Define props
const props = defineProps<{
    userId: string;
    userTypeCode: string;
}>();

</script>

<template>
    <div>
        <p>User ID: {{ props.userId }}</p>
        <p>User Type Code: {{ props.userTypeCode }}</p>
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
</style>
