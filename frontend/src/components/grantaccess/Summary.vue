<script setup lang="ts">
import Dialog from '../common/Dialog.vue';
import SummaryCard from './SummaryCard.vue';
import router from '@/router';
import {
    selectedApplicationDisplayText,
    useNotificationMessage,
    useErrorDialog,
} from '@/store/ApplicationState';
import {
    grantAccessFormData,
    resetGrantAccessFormData,
} from '@/store/GrantAccessData';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import type { FamUserRoleAssignmentCreate } from 'fam-api/dist/model/fam-user-role-assignment-create';
import { onMounted, ref } from 'vue';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const loading = ref<boolean>(false);

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;

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
        resetGrantAccessFormData();
        useErrorDialog.isErrorVisible = false;
        useNotificationMessage.isNotificationVisible = true;
        router.push('/dashboard');
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <Dialog
        v-model:visible="useErrorDialog.isErrorVisible"
        :error="true"
        header="Error"
        text-first="This role cannot be assigned to this user."
        text-second="Contact your administrator for more information."
    ></Dialog>
    <PageTitle
        title="Access request summary"
        :subtitle="'You are editing in ' + selectedApplicationDisplayText"
    />

    <div class="page-body">
        <div class="row">
            <SummaryCard
                :data="(grantAccessFormData as FamUserRoleAssignmentCreate)"
                :loading="loading"
                @submit="handleSubmit()"
            />
        </div>
    </div>
</template>
@/store/GrantAccessData
