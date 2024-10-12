<script setup lang="ts">
import { router } from "@/router";
import { Form as VeeForm } from "vee-validate";
import { computed, ref } from "vue";

import Button from "@/components/common/Button.vue";
import ForestClientInput from "@/components/grantaccess/form/ForestClientInput.vue";
import UserDomainSelect from "@/components/grantaccess/form/UserDomainSelect.vue";
import UserNameInput from "@/components/grantaccess/form/UserNameInput.vue";
import { IconSize } from "@/enum/IconEnum";
import { IdpProvider } from "@/enum/IdpEnum";
import { ErrorCode, GrantPermissionType, Severity } from "@/enum/SeverityEnum";
import { TabKey } from "@/enum/TabEnum";
import { routeItems } from "@/router/RouteItems";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import {
    formValidationSchema,
    isProdAppSelectedOnProdEnv,
} from "@/services/utils";
import {
    selectedApplicationDisplayText,
    selectedApplicationId,
} from "@/store/ApplicationState";
import { setCurrentTabState } from "@/store/CurrentTabState";
import FamLoginUserState from "@/store/FamLoginUserState";
import { isLoading } from "@/store/LoadingState";
import {
    composeAndPushGrantPermissionNotification,
    setNotificationMsg,
} from "@/store/NotificationState";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import {
    EmailSendingStatus,
    type FamUserRoleAssignmentCreateSchema,
} from "fam-app-acsctl-api";
import { UserType } from "fam-app-acsctl-api/model";

const defaultDomain =
    FamLoginUserState.getUserIdpProvider() === IdpProvider.IDIR
        ? UserType.I
        : UserType.B;

const defaultFormData = {
    domain: defaultDomain,
    userId: "",
    userGuid: "",
    verifiedForestClients: [],
    roleId: null as number | null,
    sendUserEmail: isProdAppSelectedOnProdEnv() as boolean,
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
    formData.value.userId = "";
    formData.value.userGuid = "";
};

const userIdChange = (userId: string) => {
    formData.value.userId = userId;
    formData.value.userGuid = "";
};

const verifyUserIdPassed = ref(false);
const setVerifyUserIdPassed = (
    verifiedResult: boolean,
    userGuid: string = "",
    userEmail: string = ""
) => {
    verifyUserIdPassed.value = verifiedResult;
    formData.value.userGuid = userGuid;
    formData.value.userEmail = userEmail;
};

/* ------------------- Role selection method -------------------------- */
const getSelectedRole = (): FamRoleDto | undefined => {
    return applicationRoleOptions?.value.find(
        (item) => item.id === formData.value.roleId
    );
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.type_code == "A";
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
    router.push("/manage-permissions");
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
    const newUserAccessIds: number[] = [];
    let errorCode = ErrorCode.Default;
    const data = toRequestPayload(formData.value);

    // when we assign a concrete a role to the user, there is no forest client number,
    // we add an empty string to the success or error list,
    // so the successList or errorList will be [''] for granting concrete role,
    // or ["00001011", "00001012", ...] for granting abstract role,
    // the composeAndPushGrantPermissionNotification method will handle both cases
    try {
        const returnResponse =
            await AppActlApiService.userRoleAssignmentApi.createUserRoleAssignmentMany(
                data
            );

        returnResponse.data.assignments_detail.forEach((response) => {
            const forestClientNumber =
                response.detail.role.forest_client?.forest_client_number;
            if (response.status_code == 200) {
                newUserAccessIds.push(response.detail.user_role_xref_id);
                successList.push(forestClientNumber ?? "");
            } else {
                if (response.status_code == 409) errorCode = ErrorCode.Conflict;
                errorList.push(forestClientNumber ?? "");
            }
        });

        if (
            returnResponse.data.email_sending_status ==
            EmailSendingStatus.SentToEmailServiceFailure
        ) {
            setNotificationMsg(
                Severity.Error,
                `Failed to send email to ${formData.value.userEmail}, please contact the user to notify they've been granted permission.`
            );
        }
    } catch (error: any) {
        // error happens here will fail adding all forest client numbers
        if (error.response?.data.detail.code === "self_grant_prohibited") {
            errorCode = ErrorCode.SelfGrantProhibited;
        }
        // if has forest clientn number, set errorList to be the verifiedForestClients list
        // if not, set to be [''] for concrete role, the composeAndPushGrantPermissionNotification will handle both cases
        errorList =
            formData.value.verifiedForestClients.length > 0
                ? formData.value.verifiedForestClients
                : [""];
    }

    composeAndPushGrantPermissionNotification(
        GrantPermissionType.Regular,
        username,
        successList,
        errorList,
        errorCode,
        role
    );

    setCurrentTabState(TabKey.UserAccess);

    // TODO if (newUserAccessIds.length > 0) {
    //     hashRouter.push({
    //         path: routeItems.dashboard.path,
    //         query: {
    //             newUserAccessIds: newUserAccessIds.join(","),
    //         },
    //     });
    // } else {
    //     hashRouter.push(routeItems.dashboard.path);
    // }
};

function toRequestPayload(formData: any) {
    const request = {
        user_name: formData.userId,
        user_guid: formData.userGuid,
        user_type_code: formData.domain,
        role_id: formData.roleId,
        requires_send_user_email: formData.sendUserEmail,
        ...(formData.verifiedForestClients.length > 0
            ? {
                  forest_client_numbers: formData.verifiedForestClients,
              }
            : {}),
    } as FamUserRoleAssignmentCreateSchema;
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
                        v-if="
                            FamLoginUserState.getUserIdpProvider() ===
                            IdpProvider.IDIR
                        "
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
                    title="User roles"
                    :divider="isAbstractRoleSelected()"
                >
                    <RoleSelectTable
                        :roleId="formData.roleId"
                        :roleOptions="applicationRoleOptions"
                        @change="roleSelectChange"
                        @resetVerifiedForestClients="resetVerifiedForestClients"
                    />
                </StepContainer>

                <StepContainer
                    v-if="isAbstractRoleSelected()"
                    title="Organization information"
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

                <Divider />
                <BoolCheckbox
                    v-model="formData.sendUserEmail"
                    label="Send email to notify user"
                />

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
