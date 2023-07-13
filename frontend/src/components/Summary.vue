<script setup lang="ts">
import {
    selectedApplicationDisplayText,
    grantAccessFormData,
} from '@/store/ApplicationState';
import { ref } from 'vue';
import router from '@/router';
import { useToast } from 'vue-toastification';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import type { FamUserRoleAssignmentCreate } from 'fam-api/dist/model/fam-user-role-assignment-create';
import type { FamApplicationRole } from 'fam-api';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.
const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumber: '',
    role_id: null,
};
let applicationRoleOptions = ref<FamApplicationRole[]>([]);

async function handleSubmit() {
    try {
        await userRoleAssignmentApi.createUserRoleAssignment(
            grantAccessFormData.value as FamUserRoleAssignmentCreate
        );
        useToast().success(
            `User "${grantAccessFormData?.value?.user_name}" is granted with "${
                getSelectedRole()?.role_name
            }" access.`
        );
        grantAccessFormData.value = JSON.parse(JSON.stringify(defaultFormData)); // clone default input data.
        router.push('/dashboard');
    } catch (err: any) {
        return Promise.reject(err);
    }
}

const getSelectedRole = (): FamApplicationRole | undefined => {
    return applicationRoleOptions.value.find(
        (item) => item.role_id === grantAccessFormData?.value?.role_id
    );
};
</script>

<template>
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
