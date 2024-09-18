<script setup lang="ts">
import { useRoute } from 'vue-router';
import { hashRouter } from '@/router';
import UserInfoCard from '@/components/UserInfoCard';

const route = useRoute();

// Access the path parameters
const userId = route.params.userId as string | undefined;
const applicationId = route.params.applicationId as string | undefined;
const userTypeCode = route.params.userTypeCode as string | undefined;

if (!userId || !applicationId || !userTypeCode) {
  console.warn("Missing required path params");
  hashRouter.push('/');
}

</script>

<template>
  <UserInfoCard :userId="userId" :userTypeCode="userTypeCode" />
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
</style>
