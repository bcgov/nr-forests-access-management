<script setup lang="ts">
import SummaryCard from '@/components/grantaccess/SummaryCard.vue';
import router from '@/router';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';
import { onMounted } from 'vue';

import { notificationMessageState } from '@/store/NotificationState';

import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    grantAccessFormData,
    grantAccessFormRoleName,
    resetGrantAccessFormData,
} from '@/store/GrantAccessDataState';
import type { FamUserRoleAssignmentCreate } from 'fam-api/dist/model/fam-user-role-assignment-create';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();

onMounted(() => {
    if (!grantAccessFormData.value) {
        router.push('/dashboard');
    }
});

async function handleSubmit() {
    await userRoleAssignmentApi.createUserRoleAssignment(
        grantAccessFormData.value as FamUserRoleAssignmentCreate
    );
    notificationMessageState.isVisible = true;
    router.push('/dashboard');
    resetGrantAccessFormData();
}
</script>

<template>
    <PageTitle
        title="Access request summary"
        :subtitle="'You are editing in ' + selectedApplicationDisplayText"
    />

    <div class="page-body">
        <SummaryCard
            v-if="grantAccessFormData"
            :data="(grantAccessFormData as FamUserRoleAssignmentCreate)"
            :role_name="(grantAccessFormRoleName as string)"
            @submit="handleSubmit()"
        />
    </div>
</template>
