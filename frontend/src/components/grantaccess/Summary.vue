<script setup lang="ts">
import { onMounted, ref } from 'vue';
import router from '@/router';
import SummaryCard from './SummaryCard.vue';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';

import { useNotificationMessage } from '@/store/NotificationState';

import {
    grantAccessFormData,
    resetGrantAccessFormData,
    grantAccessFormRoleName,
} from '@/store/GrantAccessDataState';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import type { FamUserRoleAssignmentCreate } from 'fam-api/dist/model/fam-user-role-assignment-create';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const loading = ref<boolean>(false);

onMounted(() => {
    if (!grantAccessFormData.value) {
        router.push('/dashboard');
    }
});

async function handleSubmit() {
    try {
        loading.value = true;
        await userRoleAssignmentApi.createUserRoleAssignment(
            grantAccessFormData.value as FamUserRoleAssignmentCreate
        );
        useNotificationMessage.isNotificationVisible = true;
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
        router.push('/dashboard');
        resetGrantAccessFormData();
        loading.value = false;
    }
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
            :loading="loading"
            @submit="handleSubmit()"
        />
    </div>
</template>
