<script setup lang="ts">
import { ref, computed } from 'vue';
import router from '@/router';
import { Form as VeeForm } from 'vee-validate';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { isLoading } from '@/store/LoadingState';
import LoginUserState from '@/store/FamLoginUserState';
import { selectedApplicationId } from '@/store/ApplicationState';
import { UserType } from 'fam-app-acsctl-api';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';
import { formValidationSchema } from '@/services/utils';

const defaultFormData = {
    domain: UserType.I,
    userId: '',
    verifiedForestClients: [],
    roleId: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input

const delegatedRoleOptions = computed(() => {
    return LoginUserState.getCachedAppRoles(selectedApplicationId.value!);
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
    return delegatedRoleOptions?.value.find(
        (item) => item.id === formData.value.roleId
    );
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.type_code == 'A';
};

const roleSelectChange = (roleId: number) => {
    formData.value.roleId = roleId;
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
    // This will be implemented in task #1160
    console.log('Data to send to backend', formData.value);

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
        v-slot="{ meta }"
        :validation-schema="formValidationSchema(isAbstractRoleSelected())"
        as="div"
    >
        <div class="page-body">
            <form id="grantDelegatedForm" class="form-container">
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
                    <RoleSelect
                        :roleId="formData.roleId"
                        :roleOptions="delegatedRoleOptions"
                        label="Assign a role the delgated admin can manage"
                        @change="roleSelectChange"
                        @resetVerifiedForestClients="resetVerifiedForestClients"
                    />
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
                        id="grantDelegatedCancel"
                        class="w100"
                        severity="secondary"
                        label="Cancel"
                        :disabled="isLoading()"
                        @click="cancelForm()"
                        >&nbsp;</Button
                    >
                    <Button
                        type="button"
                        id="grantDelegatedSubmit"
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