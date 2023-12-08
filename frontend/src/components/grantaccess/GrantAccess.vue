<script setup lang="ts">
import router from '@/router';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { onMounted, ref } from 'vue';
import { number, object, string } from 'yup';
import Dropdown from 'primevue/dropdown';

import ApiServiceFactory from '@/services/ApiServiceFactory';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { Severity } from '@/enum/SeverityEnum';
import { setGrantAccessNotificationMsg } from '@/store/NotificationState';
import {
    selectedApplication,
    selectedApplicationDisplayText,
} from '@/store/ApplicationState';
import LoadingState from '@/store/LoadingState';
import {
    type FamApplicationRole,
    type FamUserRoleAssignmentCreate,
    UserType,
} from 'fam-app-acsctl-api';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import ForestClientInput from '@/components/grantaccess/form/ForestClientInput.vue';
import { requireInjection } from '@/services/utils';

// Inject App Access Control Api service
const appActlApiService = requireInjection(
    ApiServiceFactory.APP_ACCESS_CONTROL_API_SERVICE_KEY
);

const defaultFormData = {
    domain: UserType.I,
    userId: '',
    verifiedForestClients: [],
    role_id: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const formValidationSchema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    role_id: number().required('Please select a value'),
    forestClientNumbers: string()
        .when('role_id', {
            is: (_role_id: number) => isAbstractRoleSelected(),
            then: () =>
                string()
                    .nullable()
                    .transform((curr, orig) => (orig === '' ? null : curr)) // Accept either null or value
                    .matches(/^[0-9,\b]+$/, 'Please enter a digit or comma')
                    .matches(
                        /^\d{8}(,?\d{8})*$/,
                        'Please enter a Forest Client ID with 8 digits long'
                    ),
        })
        .nullable(),
});

const applicationRoleOptions = ref<FamApplicationRole[]>([]);

onMounted(async () => {
    applicationRoleOptions.value = (
        await appActlApiService.applicationsApi.getFamApplicationRoles(
            selectedApplication.value?.application_id as number
        )
    ).data;
});

/* ------------------ User information method ------------------------- */
const userDomainChange = (selectedDomain: string) => {
    formData.value.domain = selectedDomain;
    formData.value.userId = '';
};

const userIdChange = (userId: string) => {
    formData.value.userId = userId;
};

const verifyUserIdPassed = ref(false);
const setVerifyUserIdPassed = (verifiedResult: boolean) => {
    verifyUserIdPassed.value = verifiedResult;
};

/* ------------------- Role selection method -------------------------- */
const getSelectedRole = (): FamApplicationRole | undefined => {
    return applicationRoleOptions.value?.find(
        (item) => item.role_id === formData.value.role_id
    );
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.role_type_code == 'A';
};

/* ----------------- Forest client number method ----------------------- */
const setVerifiedForestClients = (verifiedForestClientNumber: string) => {
    formData.value.verifiedForestClients.push(verifiedForestClientNumber);
};

const removeVerifiedForestClients = (index: number) => {
    formData.value.verifiedForestClients.splice(index, 1);
};

const resetVerifiedForestClients = () => {
    formData.value.verifiedForestClients = [];
};

/* ---------------------- Form method ---------------------------------- */

const cancelForm = () => {
    formData.value = defaultFormData;
    router.push('/dashboard');
};

/*
Two verifications are cunnretly in place: userId and forestClientNumber.
*/
const areVerificationsPassed = () => {
    return (
        // userId verification
        verifyUserIdPassed.value &&
        // forestClientNumber verification
        (!isAbstractRoleSelected() ||
            (isAbstractRoleSelected() &&
                formData.value.verifiedForestClients.length > 0))
    );
};

const handleSubmit = async () => {
    const successForestClientIdList: string[] = [];
    const warningForestClientIdList: string[] = [];

    // msg override the default error notification message
    const errorNotification = {
        msg: '',
        errorForestClientIdList: [] as string[],
    };
    do {
        const forestClientNumber = formData.value.verifiedForestClients.pop();
        const data = toRequestPayload(formData.value, forestClientNumber);
        await appActlApiService.userRoleAssignmentApi
            .createUserRoleAssignment(data)
            .then(() => {
                successForestClientIdList.push(forestClientNumber);
            })
            .catch((error) => {
                if (error.response?.status === 409) {
                    warningForestClientIdList.push(forestClientNumber);
                } else if (
                    error.response.data.detail.code === 'self_grant_prohibited'
                ) {
                    errorNotification.msg =
                        'Granting roles to self is not allowed.';
                } else {
                    errorNotification.errorForestClientIdList.push(
                        forestClientNumber
                    );
                }
            });
    } while (formData.value.verifiedForestClients.length > 0);

    composeAndPushNotificationMessages(
        successForestClientIdList,
        warningForestClientIdList,
        errorNotification
    );

    router.push('/dashboard');
};

function toRequestPayload(formData: any, forestClientNumber: string) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role_id,
        forest_client_number: forestClientNumber,
    } as FamUserRoleAssignmentCreate;
    return request;
}

const composeAndPushNotificationMessages = (
    successIdList: string[],
    warningIdList: string[],
    errorMsg: { msg: string; errorForestClientIdList: string[] }
) => {
    const username = formData.value.userId.toUpperCase();
    if (successIdList.length > 0) {
        setGrantAccessNotificationMsg(
            successIdList,
            username,
            Severity.success,
            getSelectedRole()?.role_name
        );
    }
    if (warningIdList.length > 0) {
        setGrantAccessNotificationMsg(
            warningIdList,
            username,
            Severity.warning,
            getSelectedRole()?.role_name
        );
    }

    if (errorMsg.msg) {
        setGrantAccessNotificationMsg(
            errorMsg.errorForestClientIdList,
            username,
            Severity.error,
            getSelectedRole()?.role_name,
            `An error has occured. ${errorMsg.msg}`
        );
    } else if (errorMsg.errorForestClientIdList.length > 0) {
        setGrantAccessNotificationMsg(
            errorMsg.errorForestClientIdList,
            username,
            Severity.error,
            getSelectedRole()?.role_name
        );
    }
    return '';
};
</script>

<template>
    <PageTitle
        title="Add user permission"
        subtitle="Add a new permission to a user. All fields are mandatory unless noted"
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
                    :subtitle="`Enter the user information to add a new user to ${selectedApplicationDisplayText}`"
                >
                    <UserDomainSelect
                        :domain="formData.domain"
                        @change="userDomainChange"
                    />
                    <UserNameInput
                        :domain="formData.domain"
                        :userId="formData.userId"
                        @change="userIdChange"
                        @setVerifyResult="setVerifyUserIdPassed"
                    />
                </StepContainer>

                <StepContainer
                    title="Add user roles"
                    subtitle="Enter a specific role for this user"
                    :divider="isAbstractRoleSelected()"
                >
                    <label>Assign a role to the user</label>

                    <Field
                        name="role_id"
                        aria-label="Role Select"
                        v-slot="{ field, handleChange }"
                        v-model="formData.role_id"
                    >
                        <Dropdown
                            :options="applicationRoleOptions"
                            optionLabel="role_name"
                            optionValue="role_id"
                            :modelValue="field.value"
                            placeholder="Choose an option"
                            class="w-100 custom-input"
                            style="width: 100% !important"
                            v-bind="field.value"
                            @update:modelValue="handleChange"
                            :class="{
                                'is-invalid': errors.role_id,
                            }"
                        >
                        </Dropdown>
                    </Field>
                    <ErrorMessage class="invalid-feedback" name="role_id">
                    </ErrorMessage>
                </StepContainer>

                <StepContainer
                    v-if="isAbstractRoleSelected()"
                    title="Organization information"
                    subtitle="Associate one or more Client IDs to this user"
                    :divider="false"
                >
                    <ForestClientInput
                        :userId="formData.userId"
                        :roleId="formData.roleId"
                        @setVerifiedForestClients="setVerifiedForestClients"
                        @removeVerifiedForestClients="
                            removeVerifiedForestClients
                        "
                        @resetVerifiedForestClients="resetVerifiedForestClients"
                    />
                </StepContainer>

                <div class="button-stack">
                    <Button
                        type="button"
                        id="grantAccessCancel"
                        class="button w100"
                        severity="secondary"
                        label="Cancel"
                        :disabled="LoadingState.isLoading.value"
                        @click="cancelForm()"
                        >&nbsp;</Button
                    >
                    <Button
                        type="button"
                        id="grantAccessSubmit"
                        class="button w100"
                        label="Submit Application"
                        :disabled="
                            !(meta.valid && areVerificationsPassed()) ||
                            LoadingState.isLoading.value
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
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.text-danger {
    font-weight: normal;
}

.button {
    width: 7.875rem;
}

.button-stack {
    padding: 0;
    margin-top: 3rem;
    margin-bottom: 2.5rem;
    gap: 1rem;
    width: 100%;
    display: inline-grid;
    grid-template-columns: 1fr 1fr;

    Button {
        width: auto !important;
    }
}

.input-with-verify-field {
    padding: 0;
    display: block;
    width: 100%;
}

.no-label-column {
    margin-top: 1.5rem;
}

.user-radio-group {
    margin-bottom: 1.5rem;
}

.custom-input {
    max-height: 2.813rem !important;
}

@media (min-width: 390px) {
    .input-with-verify-field {
        display: inline-grid;
        grid-template-columns: auto min-content;
    }
}

@media (min-width: 768px) {
    .button-stack {
        width: 100% !important;
        grid-template-columns: 1fr 1fr;
    }

    .input-with-verify-field {
        display: inline-grid;
        grid-template-columns: auto min-content;
    }
}

@media (min-width: 1024px) {
    .button-stack {
        justify-content: start;
        grid-template-columns: auto auto;
        width: 38rem;

        Button {
            width: 15rem !important;
            gap: 2rem;
            white-space: nowrap;
        }
    }

    .input-with-verify-field {
        width: 38rem;
    }
}
</style>
