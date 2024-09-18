<script setup lang="ts">
import { useRoute } from 'vue-router';
import { hashRouter } from '@/router';
import UserSummaryCard from '@/components/UserSummaryCard/index.vue';
import type { UserTypeCodeType } from '@/types/UserTypeCodeType';

const route = useRoute();

// Access the path parameters
const userName = route.params.userName as string | undefined;
const applicationId = route.params.applicationId as string | undefined;
const userTypeCode = route.params.userTypeCode as UserTypeCodeType | undefined;

if (!userName || !applicationId || !userTypeCode) {
  console.warn("Missing required path params");
  hashRouter.push('/');
}

</script>

<template>
  <UserSummaryCard :userName="userName!" :applicationId="applicationId!" :userTypeCode="userTypeCode!" />
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
</style>
