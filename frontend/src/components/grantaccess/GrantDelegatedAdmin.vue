<script setup lang="ts">
import { ref, type PropType } from 'vue';
import router from '@/router';
import { number, object, string } from 'yup';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';

import { UserType, type FamUserRoleAssignmentCreate } from 'fam-app-acsctl-api';

import Dropdown from 'primevue/dropdown';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { Severity, ErrorCode } from '@/enum/SeverityEnum';
import { AppActlApiService } from '@/services/ApiServiceFactory';

import { FOREST_CLIENT_INPUT_MAX_LENGTH } from '@/store/Constants';
import { isLoading } from '@/store/LoadingState';
import { setGrantAccessNotificationMsg } from '@/store/NotificationState';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';

const props = defineProps({
    delegatedRoleOptions: {
        // options fetched from route.
        type: Array as PropType<FamRoleDto[]>,
    },
});

const defaultFormData = {
    domain: UserType.I,
    userId: '',
    verifiedForestClients: [],
    roleId: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const formValidationSchema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    roleId: number().required('Please select a value'),
    forestClientNumbers: string()
        .when('roleId', {
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
const getSelectedRole = (): FamRoleDto | undefined => {
    return props.delegatedRoleOptions?.find(
        (item) => item.id === formData.value.roleId
    );
    return undefined;
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.type_code == 'A';
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
    // TODO: This will be implemented in task #1160

    router.push('/dashboard');
};
</script>

<template>
    <PageTitle
        title="Add a delegated admin"
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
                    title="Add the role a delegated admin can assign"
                    :divider="isAbstractRoleSelected()"
                >
                    <label>Assign a role to the user</label>

                    <Field
                        name="roleId"
                        aria-label="Role Select"
                        v-slot="{ field, handleChange }"
                        v-model="formData.roleId"
                    >
                        <Dropdown
                            :options="delegatedRoleOptions"
                            optionLabel="name"
                            optionValue="id"
                            :modelValue="field.value"
                            placeholder="Choose an option"
                            class="w-100 custom-height"
                            style="width: 100% !important"
                            v-bind="field.value"
                            @update:modelValue="handleChange"
                            @change="resetVerifiedForestClients"
                            :class="{
                                'is-invalid': errors.roleId,
                            }"
                        />
                    </Field>
                    <ErrorMessage class="invalid-feedback" name="roleId" />
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
