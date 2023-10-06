<script setup lang="ts">
import SummaryCard from '@/components/grantaccess/SummaryCard.vue';
import router from '@/router';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';
import { onMounted } from 'vue';

import {
    successNotificationMessage,
    errorNotificationMessage,
    warningNotificationMessage,
} from '@/store/NotificationState';

import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    grantAccessFormData,
    grantAccessFormRoleName,
    resetGrantAccessFormData,
    type FamUserRoleAssignment,
} from '@/store/GrantAccessDataState';

const apiServiceFactory = new ApiServiceFactory();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();

onMounted(() => {
    if (!grantAccessFormData.value) {
        router.push('/dashboard');
    }
});

async function handleSubmit() {
    if (grantAccessFormData.value!.forest_client_number_list.length > 0) {
        const successList: string[] = [];
        const warningList: string[] = [];
        const errorList: string[] = [];
        for (const item of grantAccessFormData.value!
            .forest_client_number_list) {
            const data = {
                user_name: grantAccessFormData.value?.user_name,
                role_id: grantAccessFormData.value?.role_id,
                user_type_code: grantAccessFormData.value?.user_type_code,
                forest_client_number: item.forest_client_number,
            };

            await userRoleAssignmentApi
                .createUserRoleAssignment(data as FamUserRoleAssignment)
                .then((data) => {
                    successList.push(item.forest_client_number);
                })
                .catch((error) => {
                    if (error.response?.status === 409) {
                        warningList.push(item.forest_client_number);
                    } else {
                        errorList.push(item.forest_client_number);
                    }
                });
        }

        if (successList.length > 0) {
            successNotificationMessage.notificationMsg = `${
                grantAccessFormData.value!.user_name
            } was successfully added with Client IDs: ${successList.join(
                ', '
            )}`;
        }
        if (warningList.length > 0) {
            warningNotificationMessage.notificationMsg = `${
                grantAccessFormData.value!.user_name
            } already exists with Client IDs: ${warningList.join(', ')}`;
        }
        if (errorList.length > 0) {
            errorNotificationMessage.notificationMsg = `${
                grantAccessFormData.value!.user_name
            } was not added with Client IDs: ${errorList.join(', ')}`;
        }

        router.push('/dashboard');
        resetGrantAccessFormData();
    } else {
        await userRoleAssignmentApi.createUserRoleAssignment(
            grantAccessFormData.value as FamUserRoleAssignment
        );
        successNotificationMessage.notificationMsg = `${
            grantAccessFormData.value!.user_name
        } was successfully added with the role ${
            grantAccessFormRoleName.value
        }`;
        router.push('/dashboard');
        resetGrantAccessFormData();
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
            :data="(grantAccessFormData as FamUserRoleAssignment)"
            :role_name="(grantAccessFormRoleName as string)"
            @submit="handleSubmit()"
        />
    </div>
</template>
