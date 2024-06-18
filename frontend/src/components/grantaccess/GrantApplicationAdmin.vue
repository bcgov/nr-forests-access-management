<script setup lang="ts">
import { computed, ref } from 'vue';
import router from '@/router';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { object, string } from 'yup';
import Dropdown from 'primevue/dropdown';
import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import type { FamAppAdminCreateRequest } from 'fam-admin-mgmt-api/model/fam-app-admin-create-request';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { Severity, ErrorDescription } from '@/enum/SeverityEnum';
import { TabKey } from '@/enum/TabEnum';
import { isLoading } from '@/store/LoadingState';
import { setNotificationMsg } from '@/store/NotificationState';
import LoginUserState from '@/store/FamLoginUserState';
import { setCurrentTabState } from '@/store/CurrentTabState';
import { routeItems } from '@/router/routeItem';
import { UserType } from 'fam-app-acsctl-api/model';

const defaultFormData = {
    userId: '',
    userGuid: '',
    application: null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const formValidationSchema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    application: object().required('Application is required'),
});

const applicationOptions = computed(() => {
    return LoginUserState.getAppsForFamAdminRole();
});

/* ------------------ User information method ------------------------- */
const userIdChange = (userId: string) => {
    formData.value.userId = userId;
    formData.value.userGuid = '';
};

const verifyUserIdPassed = ref(false);
const setVerifyUserIdPassed = (
    verifiedResult: boolean,
    userGuid: string = ''
) => {
    verifyUserIdPassed.value = verifiedResult;
    formData.value.userGuid = userGuid;
};
/* ---------------------- Form method ---------------------------------- */
const cancelForm = () => {
    formData.value = defaultFormData;
    router.push('/dashboard');
};

const toRequestPayload = (formData: any) => {
    const request = {
        user_name: formData.userId,
        user_guid: formData.userGuid,
        application_id: formData.application.id,
        user_type_code: UserType.I,
    } as FamAppAdminCreateRequest;
    return request;
};

const handleSubmit = async () => {
    const data = toRequestPayload(formData.value);
    const appEnv = formData.value.application.env
        ? ` ${formData.value.application.env}`
        : '';
    let newAppAdminId = null;

    try {
        const newAppAdminReturn =
            await AdminMgmtApiService.applicationAdminApi.createApplicationAdmin(
                data
            );
        newAppAdminId = newAppAdminReturn.data.application_admin_id;
        setNotificationMsg(
            Severity.Success,
            `Admin privilege has been added to ${formData.value.userId.toUpperCase()} for application ${
                formData.value.application.name
            }${appEnv}`
        );
    } catch (error: any) {
        if (error.response?.status === 409) {
            setNotificationMsg(
                Severity.Error,
                `${formData.value.userId.toUpperCase()} is already a ${
                    formData.value.application.name
                }${appEnv} admin`
            );
        } else if (
            error.response?.data.detail.code === 'self_grant_prohibited'
        ) {
            setNotificationMsg(
                Severity.Error,
                ErrorDescription.SelfGrantProhibited
            );
        } else {
            const errorMsg = error.response?.data.detail.description
                ? ` ${error.response?.data.detail.description}`
                : ' ';
            setNotificationMsg(
                Severity.Error,
                `${
                    ErrorDescription.Default
                }${errorMsg} ${formData.value.userId.toUpperCase()} was not added as ${
                    formData.value.application.name
                }${appEnv} admin`
            );
        }
    }

    setCurrentTabState(TabKey.AdminAccess);

    if (newAppAdminId) {
        router.push({
            path: `/${routeItems.dashboard.name}`,
            query: { newAppAdminId: newAppAdminId.toString() },
        });
    } else {
        router.push(`/${routeItems.dashboard.name}`);
    }
};
</script>
<template>
    <PageTitle
        title="Add application admin"
        subtitle="All fields are mandatory"
    />
    <VeeForm
        ref="form"
        v-slot="{ errors, meta }"
        :validation-schema="formValidationSchema"
        as="div"
    >
        <div class="page-body">
            <form id="grantAdminForm" class="form-container">
                <StepContainer title="User information">
                    <UserNameInput
                        :domain="UserType.I"
                        :userId="formData.userId"
                        helper-text="Only IDIR users are allowed to be added as application admins"
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
                            <label for="application-dropdown"
                                >Select application</label
                            >
                            <Dropdown
                                v-model="formData.application"
                                :options="applicationOptions"
                                optionLabel="description"
                                placeholder="Choose an application"
                                name="application-dropdown"
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
                        id="grantAdminCancel"
                        class="w100"
                        severity="secondary"
                        label="Cancel"
                        :disabled="isLoading()"
                        @click="cancelForm()"
                        >&nbsp;</Button
                    >
                    <Button
                        type="button"
                        id="grantAdminSubmit"
                        class="w100"
                        label="Create Application Admin"
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
