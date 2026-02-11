import { IdpProvider } from "@/enum/IdpEnum";
import type { TextInputType } from "@/types/InputTypes";
import type { SelectUser } from "@/types/SelectUserType";
import {
    RoleType,
    type FamAccessControlPrivilegeCreateRequest,
    type FamGrantDetailDto,
    type FamRoleGrantDto,
} from "fam-admin-mgmt-api/model";
import {
    UserType,
    type FamForestClientSchema,
    type FamUserRoleAssignmentCreateSchema,
} from "fam-app-acsctl-api/model";
import { array, mixed, object } from "yup";

export const AddAppUserPermissionSuccessQuerykey = "app-user-mutation-success";
export const AddAppUserPermissionErrorQuerykey = "app-user-mutation-error";
export const AddDelegatedAdminSuccessQuerykey = "delegated-admin-mutation-success";
export const AddDelegatedAdminErrorQuerykey = "delegated-admin-mutation-error";

// Query Param keys for new ids
export const NewRegularUserQueryParamKey = "newRegularUserIds";
export const NewDelegatedAddminQueryParamKey = "newDelegatedAdminIds";

export const MAX_USERS_GRANTING_ALLOWED = 50;

export type AppPermissionFormType = {
    domain: UserType;
    users: SelectUser[];
    forestClients: FamForestClientSchema[];
    role: FamRoleGrantDto | null;
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
    expiryDate?: string | null; // Optional expiry date for permissions
};

export type AppPermissionQueryErrorType = {
    error: Error;
    formData: AppPermissionFormType;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    users: [],
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
    expiryDate: null,
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
export const validateAppPermissionForm = () => {
    return object({
        users: array()
            .of(mixed<SelectUser>().required("A valid user is required"))
            .max(MAX_USERS_GRANTING_ALLOWED, `User list exceeds ${MAX_USERS_GRANTING_ALLOWED} users allowed`)
            .when("isAddingDelegatedAdmin", {
                is: false,
                then: (schema) => schema.min(1, "At least one user is required"),
                otherwise: (schema) =>
                    schema
                        .min(1, "A valid user is required")
                        .max(1, "Only one user is allowed for delegated admin"),
            }),
        role: mixed<FamRoleGrantDto>().required("Please select a role"),
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
                is: (role: FamRoleGrantDto | null) =>
                    role?.type_code === RoleType.A,
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
    ): FamUserRoleAssignmentCreateSchema | FamAccessControlPrivilegeCreateRequest => {
        const common_payload = {
            user_type_code: formData.domain,
            role_id: formData.role?.id ?? -1,
            forest_client_numbers: (formData.forestClients ?? []).map(
                (fc) => fc.forest_client_number
            ),
            requires_send_user_email: formData.sendUserEmail,
            expiry_date_date: formData.expiryDate ?? null,
        };

        if (formData.isAddingDelegatedAdmin) {
            const delegatedAdminUser = formData.users[0];
            return {
                ...common_payload,
                user_name: delegatedAdminUser?.userId ?? "",
                user_guid: delegatedAdminUser?.guid ?? "",
            };
        }
        return {
            ...common_payload,
            users: formData.users.map((user) => ({
                user_guid: user.guid ?? "",
                user_name: user.userId ?? "",
            })),
        };
    };

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
): boolean => formData?.role?.type_code === RoleType.A;

export const getUserNameInputHelperText = (domain: UserType) =>
    `Type user's ${
        domain === UserType.I
            ? IdpProvider.IDIR
            : IdpProvider.BCEIDBUSINESS
    } and click "Verify username"`;