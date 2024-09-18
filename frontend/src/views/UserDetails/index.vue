<script setup lang="ts">
import { useRoute } from 'vue-router';
import { hashRouter } from '@/router';
import type { UserTypeCodeType } from '@/types/UserTypeCodeType';
import UserSummaryCard from '@/components/UserSummaryCard/index.vue';
import PageTitle from '@/components/common/PageTitle.vue';

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
  <PageTitle class="user-detail-page-title" title="User History" />
  <UserSummaryCard :userName="userName!" :applicationId="applicationId!" :userTypeCode="userTypeCode!" />
</template>

<style lang="scss">
.user-detail-page-title {
  margin-bottom: 2rem;
}
</style>
