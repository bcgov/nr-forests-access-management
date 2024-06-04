<script setup lang="ts">
import router from '@/router';
import { Form as VeeForm } from 'vee-validate';
import { computed, ref } from 'vue';

import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { ErrorCode, GrantPermissionType } from '@/enum/SeverityEnum';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { formValidationSchema } from '@/services/utils';
import { isLoading } from '@/store/LoadingState';
import { composeAndPushGrantPermissionNotification } from '@/store/NotificationState';
import { FOREST_CLIENT_INPUT_MAX_LENGTH } from '@/store/Constants';
import {
    selectedApplicationDisplayText,
    selectedApplicationId,
} from '@/store/ApplicationState';
import { UserType, type FamUserRoleAssignmentCreate } from 'fam-app-acsctl-api';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import ForestClientInput from '@/components/grantaccess/form/ForestClientInput.vue';
import FamLoginUserState from '@/store/FamLoginUserState';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';
import { setCurrentTabState } from '@/store/CurrentTabState';
import { TabKey } from '@/enum/TabEnum';

const defaultFormData = {
    domain: UserType.I,
    userId: '',
    userGuid: '',
    verifiedForestClients: [],
    roleId: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const applicationRoleOptions = computed(() => {
    if (FamLoginUserState.isAdminOfSelectedApplication()) {
        return FamLoginUserState.getCachedAppRoles(
            selectedApplicationId.value!
        );
    } else {
        return FamLoginUserState.getCachedAppRolesForDelegatedAdmin(
            selectedApplicationId.value!
        );
    }
});

/* ------------------ User information method ------------------------- */
const userDomainChange = (selectedDomain: string) => {
    formData.value.domain = selectedDomain;
    formData.value.userId = '';
    formData.value.userGuid = '';
};

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

/* ------------------- Role selection method -------------------------- */
const getSelectedRole = (): FamRoleDto | undefined => {
    return applicationRoleOptions?.value.find(
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
    const username = formData.value.userId.toUpperCase();
    const role = getSelectedRole()?.name;
    const successList: string[] = [];
    const errorList: string[] = [];
    let errorCode = ErrorCode.Default;

    // when we assign a concrete a role to the user, there is no forest client number,
    // we add an empty string to the success or error list,
    // so the successList or errorList will be [''] for granting concrete role,
    // or ["00001011", "00001012", ...] for granting abstract role,
    // the composeAndPushGrantPermissionNotification method will handle both cases
    do {
        const forestClientNumber = formData.value.verifiedForestClients.pop();
        const data = toRequestPayload(formData.value, forestClientNumber);
        try {
            await AppActlApiService.userRoleAssignmentApi.createUserRoleAssignment(
                data
            );
            successList.push(forestClientNumber ?? '');
        } catch (error: any) {
            if (error.response?.status === 409) {
                errorCode = ErrorCode.Conflict;
            } else if (
                error.response?.data.detail.code === 'self_grant_prohibited'
            ) {
                errorCode = ErrorCode.SelfGrantProhibited;
            }
            errorList.push(forestClientNumber ?? '');
        }
    } while (formData.value.verifiedForestClients.length > 0);

    composeAndPushGrantPermissionNotification(
        GrantPermissionType.Regular,
        username,
        successList,
        errorList,
        errorCode,
        role
    );
    setCurrentTabState(TabKey.UserAccess);
    router.push('/dashboard');
};

function toRequestPayload(formData: any, forestClientNumber: string) {
    const request = {
        user_name: formData.userId,
        user_guid: formData.userGuid,
        user_type_code: formData.domain,
        role_id: formData.roleId,
        ...(forestClientNumber
            ? {
                  forest_client_number: forestClientNumber.padStart(
                      FOREST_CLIENT_INPUT_MAX_LENGTH,
                      '0'
                  ),
              }
            : {}),
    } as FamUserRoleAssignmentCreate;
    return request;
}
</script>

<template>
    <PageTitle
        title="Add user permission"
        :subtitle="`Adding user permission to ${selectedApplicationDisplayText}. All fields are mandatory`"
    />
    <VeeForm
        ref="form"
        v-slot="{ meta }"
        :validation-schema="formValidationSchema(isAbstractRoleSelected())"
        as="div"
    >
        <div class="page-body">
            <form id="grantAccessForm" class="form-container">
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
                    title="Add user roles"
                    :divider="isAbstractRoleSelected()"
                >
                    <RoleSelect
                        :roleId="formData.roleId"
                        :roleOptions="applicationRoleOptions"
                        @change="roleSelectChange"
                        @resetVerifiedForestClients="resetVerifiedForestClients"
                    />
                </StepContainer>

                <StepContainer
                    v-if="isAbstractRoleSelected()"
                    title="Organization information"
                    subtitle="Associate one or more Client IDs to this user"
                    :divider="false"
                    class="invalid"
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
                        label="Grant Access"
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
