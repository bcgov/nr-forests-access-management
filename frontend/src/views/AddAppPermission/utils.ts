import { array, mixed, object } from "yup";
import {
    UserType,
    type FamForestClientSchema,
    type FamUserRoleAssignmentCreateSchema,
    type IdimProxyBceidInfoSchema,
    type IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api/model";
import type {
    FamAccessControlPrivilegeCreateRequest,
    FamGrantDetailDto,
    FamRoleDto,
} from "fam-admin-mgmt-api/model";
import type { TextInputType } from "@/types/InputTypes";

export const AddAppUserPermissionSuccessQuerykey = "app-admin-mutation-success";
export const AddAppUserPermissionErrorQuerykey = "app-admin-mutation-error";
export const AddDelegatedAdminSuccessQuerykey =
    "delegated-admin-mutation-success";
export const AddDelegatedAdminErrorQuerykey = "delegated-admin-mutation-error";

// Query Param keys for new ids
export const NewAppAdminQueryParamKey = "newAppAdminIds";
export const NewDelegatedAddminQueryParamKey = "newDelegatedAdminIds";

export type AppPermissionFormType = {
    domain: UserType;
    user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null;
    forestClients: FamForestClientSchema[];
    role: FamRoleDto | null;
    sendUserEmail: boolean;
    forestClientInput: TextInputType & {
        /**
         * Track if a verification of a client number is in progress.
         * Disable role selection if it's verifying, otherwise a client might be added
         * right after switching.
         */
        isVerifying: boolean;
    };
    isAddingDelegatedAdmin: boolean;
};

export type AppPermissionQueryErrorType = {
    error: Error;
    formData: AppPermissionFormType;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    user: null,
    forestClients: [],
    role: null,
    sendUserEmail: false,
    forestClientInput: {
        id: "forest-client-number-input",
        value: "",
        isValid: true,
        errorMsg: "",
        isVerifying: false,
    },
    isAddingDelegatedAdmin: false,
};

export const getDefaultFormData = (
    domain: UserType,
    sendUserEmail: boolean
): AppPermissionFormType => {
    const copy = structuredClone(defaultFormData);
    return {
        ...copy,
        domain,
        sendUserEmail,
    };
};

/**
 * Validation schema for app admin and delegated admin
 */
export const validateAppPermissionForm = (isAbstractRoleSelected: boolean) => {
    return object({
        user: mixed<IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema>()
            .required("A valid user is required")
            .test("is-user-found", "A valid user ID is required", (value) => {
                return value?.found === true;
            }),
        role: mixed<FamRoleDto>().required("Please select a role"),
        forestClients: array()
            .of(
                mixed<FamForestClientSchema>()
                    .required("Each Forest Client must be a valid object")
                    .test(
                        "not-empty-object",
                        "Forest Client cannot be empty",
                        (item) => item && Object.keys(item).length > 0
                    )
            )
            .when("role", {
                is: () => isAbstractRoleSelected,
                then: (schema) =>
                    schema.min(1, "At least one organization is required"),
                otherwise: (schema) => schema.default([]).nullable(),
            }),
    });
};

/**
 * Generates a payload for creating a user role assignment or access control privilege request.
 *
 * @param {AppPermissionFormType} formData - The complete form data containing user and role details.
 * @returns {FamUserRoleAssignmentCreateSchema | FamAccessControlPrivilegeCreateRequest} a payload object.
 *
 */
export const generatePayload = (
    formData: AppPermissionFormType
):
    | FamUserRoleAssignmentCreateSchema
    | FamAccessControlPrivilegeCreateRequest => ({
    user_name: formData.user?.userId ?? "",
    user_guid: formData.user?.guid ?? "",
    user_type_code: formData.domain,
    role_id: formData.role?.id ?? -1,
    forest_client_numbers: formData.forestClients.map(
        (fc) => fc.forest_client_number
    ),
    requires_send_user_email: formData.sendUserEmail,
});

export const getRolesByAppId = (data: FamGrantDetailDto[], appId: number) => {
    const foundGrantByAppId = data.find(
        (grant) => grant.application.id === appId
    );

    if (foundGrantByAppId) {
        return {
            application: foundGrantByAppId.application,
            roles: foundGrantByAppId.roles,
        };
    }

    return null;
};

export const isAbstractRoleSelected = (
    formData?: AppPermissionFormType
): boolean => formData?.role?.type_code === "A";
