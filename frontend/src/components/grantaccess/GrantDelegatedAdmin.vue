<script setup lang="ts">
import { ref, type PropType } from 'vue';
import router from '@/router';
import { Form as VeeForm } from 'vee-validate';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { ErrorCode, GrantPermissionType } from '@/enum/SeverityEnum';
import { isLoading } from '@/store/LoadingState';
import { composeAndPushGrantPermissionNotification } from '@/store/NotificationState';
import { UserType } from 'fam-app-acsctl-api';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';
import type { FamAccessControlPrivilegeCreateRequest } from 'fam-admin-mgmt-api/model/fam-access-control-privilege-create-request';
import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { formValidationSchema } from '@/services/utils';

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
    let errorList: string[] = [];
    let errorCode = ErrorCode.Default;

    const data = toRequestPayload(formData.value);

    try {
        const returnResponse =
            await AdminMgmtApiService.delegatedAdminApi.createAccessControlPrivilegeMany(
                data
            );
        returnResponse.data.forEach((response) => {
            const forestClientNumber =
                response.detail.role.client_number?.forest_client_number;
            if (response.status_code == 200) {
                successList.push(forestClientNumber || '');
            } else {
                if (response.status_code == 409) errorCode = ErrorCode.Conflict;
                errorList.push(forestClientNumber || '');
            }
        });
    } catch (error: any) {
        // error happens here will fail adding all forest client numbers
        if (error.response.data.detail.code === 'self_grant_prohibited') {
            errorCode = ErrorCode.SelfGrantProhibited;
        }
        errorList = formData.value.verifiedForestClients;
    }
    composeAndPushGrantPermissionNotification(
        GrantPermissionType.DelegatedAdmin,
        username,
        role,
        successList,
        errorList,
        errorCode
    );
    router.push('/dashboard');
};

function toRequestPayload(formData: any) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.roleId,
        ...(formData.verifiedForestClients.length > 0
            ? {
                  forest_client_numbers: formData.verifiedForestClients,
              }
            : {}),
    } as FamAccessControlPrivilegeCreateRequest;
    return request;
}
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
