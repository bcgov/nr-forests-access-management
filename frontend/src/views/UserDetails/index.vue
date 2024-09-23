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
  <div class="user-detail-page-container">
    <PageTitle class="user-detail-page-title" title="User History" />
    <UserSummaryCard :userName="userName!" :applicationId="applicationId!" :userTypeCode="userTypeCode!" />
    <div class="gray-container">
    </div>
  </div>
</template>

<style lang="scss">
.user-detail-page-container {
  display: flex;
  flex-direction: column;
  min-height: 93vh;

  .user-detail-page-title {
    margin-bottom: 2rem;
  }

  .gray-container {
    background-color: colors.$gray-10;
    flex-grow: 1;
    margin: 2.5rem -2.5rem 0 -2.5rem;
    padding: 2.5rem;
  }
}
</style>
