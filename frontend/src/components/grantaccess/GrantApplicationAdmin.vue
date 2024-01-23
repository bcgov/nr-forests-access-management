git s<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { number, object, string } from 'yup';
import type { FamApplication } from 'fam-app-acsctl-api';
import ApplicationSelect from '@/components/grantaccess/form/ApplicationSelect.vue';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';

import { isLoading } from '@/store/LoadingState';

import {
    applicationsUserAdministers,
    selectedApplication,
    setSelectedApplication,
} from '@/store/ApplicationState';
import router from '@/router';
import { fetchUserRoleAssignments } from '@/services/fetchData';

const defaultFormData = {
    userId: '',
    application: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const formValidationSchema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    application: number().required('Application is required'),
});
onMounted(() => {});
/* ------------------ User information method ------------------------- */
const userIdChange = (userId: string) => {
    formData.value.userId = userId;
};

const verifyUserIdPassed = ref(false);
const setVerifyUserIdPassed = (verifiedResult: boolean) => {
    verifyUserIdPassed.value = verifiedResult;
};
/* ---------------------- Form method ---------------------------------- */
const cancelForm = () => {
    formData.value = defaultFormData;
    router.push('/dashboard');
};

/*
Two verifications are currently in place: userId and application.
*/
const areVerificationsPassed = () => {
    // return (
    //     // userId verification
    //     verifyUserIdPassed.value &&
    //     // forestClientNumber verification
    //     (!isAbstractRoleSelected() ||
    //         (isAbstractRoleSelected() &&
    //             formData.value.verifiedForestClients.length > 0))
    // );
    return true;
};

const handleSubmit = async () => {
    // const successForestClientIdList: string[] = [];
    // const warningForestClientIdList: string[] = [];

    // // msg override the default error notification message
    // const errorNotification = {
    //     msg: '',
    //     errorForestClientIdList: [] as string[],
    // };
    // do {
    //     const forestClientNumber = formData.value.verifiedForestClients.pop();
    //     const data = toRequestPayload(formData.value, forestClientNumber);
    //     await AppActlApiService.userRoleAssignmentApi
    //         .createUserRoleAssignment(data)
    //         .then(() => {
    //             successForestClientIdList.push(forestClientNumber || '');
    //         })
    //         .catch((error) => {
    //             if (error.response?.status === 409) {
    //                 warningForestClientIdList.push(forestClientNumber || '');
    //             } else if (
    //                 error.response.data.detail.code === 'self_grant_prohibited'
    //             ) {
    //                 errorNotification.msg =
    //                     'Granting roles to self is not allowed.';
    //             } else {
    //                 errorNotification.errorForestClientIdList.push(
    //                     forestClientNumber || ''
    //                 );
    //             }
    //         });
    // } while (formData.value.verifiedForestClients.length > 0);

    // composeAndPushNotificationMessages(
    //     successForestClientIdList,
    //     warningForestClientIdList,
    //     errorNotification
    // );

    router.push('/dashboard');
};

const onApplicationSelected = async (e: any) => {
    setSelectedApplication(e ? JSON.stringify(e) : null);
};
</script>
<template>
    <PageTitle
        title="Add application admin"
        subtitle="Add a new application admin. All fields are mandatory unless noted"
    />
    <VeeForm
        ref="form"
        v-slot="{ errors, meta }"
        :validation-schema="formValidationSchema"
        as="div"
    >
        <div class="page-body">
            <form id="grantAccessForm" class="form-container">
                <StepContainer
                    title="User information"
                    subtitle="Enter the user information to add a new admin to [Application name]"
                >
                    <UserNameInput
                        domain="I"
                        :userId="formData.userId"
                        helper-text="Only IDIR usernames are allowed"
                        @change="userIdChange"
                        @setVerifyResult="setVerifyUserIdPassed"
                    />
                </StepContainer>
                <StepContainer
                    title="Add application "
                    subtitle="Select an application this user will be able to manage"
                    :divider="false"
                >
                    <Field
                        name="application"
                        aria-label="Application Select"
                        v-model="formData.application"
                    >
                        <ApplicationSelect
                            :model="(selectedApplication as FamApplication)"
                            :options="applicationsUserAdministers"
                            @onApplicationSelected="
                                onApplicationSelected($event)
                            "
                        />
                        <ErrorMessage
                            class="invalid-feedback"
                            name="application"
                            style="display: inline"
                        />
                    </Field>
                </StepContainer>
                <div class="button-stack">
                    <Button
                        type="button"
                        id="grantAccessCancel"
                        class="w100"
                        severity="secondary"
                        label="Cancel"
                        :disabled="isLoading()"
                        @click="cancelForm()"
                        >&nbsp;</Button
                    >
                    <Button
                        type="button"
                        id="grantAccessSubmit"
                        class="w100"
                        label="Submit Application"
                        :disabled="
                            !(meta.valid && areVerificationsPassed()) ||
                            isLoading()
                        "
                        @click="handleSubmit()"
                    >
                        <Icon icon="checkmark" :size="IconSize.small" />
                    </Button>
                </div>
            </form>
        </div>
    </VeeForm>
</template>
