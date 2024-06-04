<script setup lang="ts">
import { ref, computed } from 'vue';
import { Form as VeeForm } from 'vee-validate';
import { useConfirm } from 'primevue/useconfirm';
import ConfirmDialog from 'primevue/confirmdialog';
import router from '@/router';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { ErrorCode, GrantPermissionType } from '@/enum/SeverityEnum';
import { isLoading } from '@/store/LoadingState';
import LoginUserState from '@/store/FamLoginUserState';
import { composeAndPushGrantPermissionNotification } from '@/store/NotificationState';
import {
    selectedApplicationId,
    selectedApplicationDisplayText,
} from '@/store/ApplicationState';
import { formValidationSchema } from '@/services/utils';
import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { UserType } from 'fam-app-acsctl-api';
import type {
    FamRoleDto,
    FamAccessControlPrivilegeCreateRequest,
} from 'fam-admin-mgmt-api/model';
import { setCurrentTabState } from '@/store/CurrentTabState';
import { TabKey } from '@/enum/TabEnum';
import { setNewUsers } from '@/store/newUserComparatorState';

const confirm = useConfirm();

const defaultFormData = {
    domain: UserType.I,
    userId: '',
    userGuid: '',
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

const confirmSubmit = async () => {
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
            setNewUsers(data, TabKey.DelegatedAdminAccess)
        returnResponse.data.forEach((response) => {
            const forestClientNumber =
                response.detail.role.client_number?.forest_client_number;
            if (response.status_code == 200) {
                successList.push(forestClientNumber ?? '');
            } else {
                if (response.status_code == 409) errorCode = ErrorCode.Conflict;
                errorList.push(forestClientNumber ?? '');
            }
        });
    } catch (error: any) {
        // error happens here will fail adding all forest client numbers
        if (error.response?.data.detail.code === 'self_grant_prohibited') {
            errorCode = ErrorCode.SelfGrantProhibited;
        }
        // if has forest clientn number, set errorList to be the verifiedForestClients list
        // if not, set to be [''] for concrete role, the composeAndPushGrantPermissionNotification will handle both cases
        errorList =
            formData.value.verifiedForestClients.length > 0
                ? formData.value.verifiedForestClients
                : [''];
    }
    composeAndPushGrantPermissionNotification(
        GrantPermissionType.DelegatedAdmin,
        username,
        successList,
        errorList,
        errorCode,
        role
    );
    setCurrentTabState(TabKey.DelegatedAdminAccess);
    router.push('/dashboard');
};

function toRequestPayload(formData: any) {
    const request = {
        user_name: formData.userId,
        user_guid: formData.userGuid,
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

function handleSubmit() {
    confirm.require({
        group: 'addDelegatedAdmin',
        header: 'Add a delegated admin',
        rejectLabel: 'Cancel',
        acceptLabel: 'Submit delegated admin',
        acceptClass: 'dialog-accept-button',
        accept: () => {
            confirmSubmit();
        },
    });
}
</script>

<template>
    <ConfirmDialog group="addDelegatedAdmin">
        <template #message>
            <p>
                Are you sure you want to add
                <strong>{{ formData.userId.toUpperCase() }}</strong> as a
                delegated admin? As a delegated admin
                <strong>{{ formData.userId.toUpperCase() }}</strong> will be
                able to add, edit or delete users
            </p>
        </template>
    </ConfirmDialog>

    <PageTitle
        title="Add a delegated admin"
        :subtitle="`Adding a delegated admin to ${selectedApplicationDisplayText}. All fields are mandatory`"
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
                        label="Create Delegated Admin"
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
<style lang="scss">
@use '@bcgov-nr/nr-theme/design-tokens/light-buttons.scss' as lightButton;
@use 'sass:map';

.dialog-accept-button {
    border: 0.0625rem solid
        map.get(lightButton.$light-button-token-overrides, 'button-primary') !important;
    background-color: map.get(
        lightButton.$light-button-token-overrides,
        'button-primary'
    ) !important;
}

.dialog-accept-button:hover {
    border: 0.0625rem solid
        map.get(
            lightButton.$light-button-token-overrides,
            'button-primary-hover'
        ) !important;
    background-color: map.get(
        lightButton.$light-button-token-overrides,
        'button-primary-hover'
    ) !important;
}
</style>
