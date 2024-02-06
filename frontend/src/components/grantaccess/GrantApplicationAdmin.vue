<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { object, string } from 'yup';
import router from '@/router';
import Dropdown from 'primevue/dropdown';
import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { UserType, type FamApplication } from 'fam-app-acsctl-api';
import type { FamAppAdminCreateRequest } from 'fam-admin-mgmt-api/model/fam-app-admin-create-request';
import type { FamApplicationGetResponse } from 'fam-admin-mgmt-api/model/fam-application-get-response';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { Severity } from '@/enum/SeverityEnum';

import { isLoading } from '@/store/LoadingState';
import { setNotificationMsg } from '@/store/NotificationState';

const defaultFormData = {
    userId: '',
    application: Number,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const formValidationSchema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    application: object().required('Application is required'),
});

const applications = ref<FamApplicationGetResponse[]>();

// This is going to be changed when the new backend API is ready
onMounted(async () => {
    applications.value = (
        await AdminMgmtApiService.applicationsApi.getApplications()
    ).data;
});

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

const toRequestPayload = (formData: any) => {
    const request = {
        user_name: formData.userId,
        application_id: formData.application.application_id,
        user_type_code: UserType.I,
    } as FamAppAdminCreateRequest;
    return request;
};

const handleSubmit = async () => {
    const data = toRequestPayload(formData.value);
    await AdminMgmtApiService.applicationAdminApi
        .createApplicationAdmin(data)
        .then(() => {
            setNotificationMsg(
                Severity.success,
                `Admin privilege has been added to ${formData.value.userId.toUpperCase()} for application ${
                    formData.value.application.application_name
                }`
            );
        })
        .catch((error) => {
            if (error.response?.status === 409) {
                setNotificationMsg(
                    Severity.warning,
                    error.response.data.detail
                );
            } else if (
                error.response.data.detail.code === 'self_grant_prohibited'
            ) {
                setNotificationMsg(
                    Severity.error,
                    'Granting admin privilege to self is not allowed.'
                );
            } else {
                setNotificationMsg(
                    Severity.success,
                    `An error has occured. ${error.response.data.detail.description}`
                );
            }
        })
        .finally(() => {
            router.push('/dashboard');
        });
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
            <form id="grantAdminForm" class="form-container">
                <StepContainer
                    title="User information"
                    :subtitle="`Enter the user information to add a new admin ${
                        formData.application
                            ? 'to ' + formData.application.application_name
                            : ''
                    }`"
                >
                    <UserNameInput
                        :domain="UserType.I"
                        :userId="formData.userId"
                        helper-text="Only IDIR usernames are allowed"
                        @change="userIdChange"
                        @setVerifyResult="setVerifyUserIdPassed"
                    />
                </StepContainer>
                <StepContainer
                    title="Add application"
                    subtitle="Select an application this user will be able to manage"
                    :divider="false"
                >
                    <Field
                        name="application"
                        aria-label="Application Select"
                        v-model="formData.application"
                    >
                        <div class="application-admin-group">
                            <label>Select application</label>
                            <Dropdown
                                v-model="formData.application"
                                :options="(applications as FamApplication[])"
                                optionLabel="application_description"
                                placeholder="Choose an application"
                            />
                        </div>
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
                            !(meta.valid && verifyUserIdPassed) || isLoading()
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
<style scoped lang="scss">
.application-admin-group {
    display: grid;
}
</style>
