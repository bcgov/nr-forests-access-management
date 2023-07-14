<script setup lang="ts">
import {
    selectedApplicationDisplayText,
    grantAccessFormData,
    useNotificationMessage,
} from '@/store/ApplicationState';
import { ref } from 'vue';
import router from '@/router';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import type { FamUserRoleAssignmentCreate } from 'fam-api/dist/model/fam-user-role-assignment-create';
import type { FamApplicationRole } from 'fam-api';
import { useErrorDialog } from '@/store/ApplicationState';
import Dialog from './dialog/Dialog.vue';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.
const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumber: '',
    role_id: null,
};

async function handleSubmit() {
    try {
        await userRoleAssignmentApi.createUserRoleAssignment(
            grantAccessFormData.value as FamUserRoleAssignmentCreate
        );
        grantAccessFormData.value = JSON.parse(JSON.stringify(defaultFormData)); // clone default input data.
        useErrorDialog.isErrorVisible = false;
        useNotificationMessage.isNotificationVisible = true;
        router.push('/dashboard');
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
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
                @submit="handleSubmit()"
            />
        </div>
    </div>
</template>
