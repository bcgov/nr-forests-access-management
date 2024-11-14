import { isAxiosError } from "axios";
import {
    AdminRoleAuthGroup,
    type FamAccessControlPrivilegeGetResponse,
    type FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { formatAxiosError } from "@/utils/ApiUtils";
import type { PermissionNotificationType } from "@/types/ManagePermissionsTypes";
import type { FamApplicationUserRoleAssignmentGetSchema } from "fam-app-acsctl-api/model";

export type ConfirmTextType = {
    role: string;
    userName: string;
    appName: string;
    customMsg?: string;
};

export const filterList = [
    "application.app_environment",
    "application.application_name",
    "role.client_number.forest_client_number",
    "role.forest_client.forest_client_number",
    "role.parent_role.role_name",
    "role.role_name",
    "user.email",
    "user.first_name",
    "user.last_name",
    "user.user_name",
    "user.user_type.description",
];

/**
 * Generates the header title text for the table based on the application name.
 */
export const getTableHeaderTitle = (
    appName: string,
    authGroup: AdminRoleAuthGroup
): string => {
    switch (authGroup) {
        case AdminRoleAuthGroup.FamAdmin:
            return `${appName} users`;
        case AdminRoleAuthGroup.AppAdmin:
            return `${appName} users`;
        case AdminRoleAuthGroup.DelegatedAdmin:
            return `${appName} delegated administrators`;
        default:
            return `${appName} users`;
    }
};

/**
 * Generates a description for the table header section based on the application name.
 */
export const getTableHeaderDescription = (
    appName: string,
    authGroup: AdminRoleAuthGroup
): string => {
    switch (authGroup) {
        case AdminRoleAuthGroup.FamAdmin:
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case AdminRoleAuthGroup.AppAdmin:
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case AdminRoleAuthGroup.DelegatedAdmin:
            return `
            This table shows all the delegated administrators in ${appName} and the roles they are allowed to manage for their users
            `;
        default:
            return `This table shows all the users in ${appName} and their permissions levels`;
    }
};

/**
 * Generates the label for a grant button based on the authorization group.
 */
export const getGrantButtonLabel = (authGroup: AdminRoleAuthGroup): string => {
    switch (authGroup) {
        case AdminRoleAuthGroup.FamAdmin:
            return "Add application admin";
        case AdminRoleAuthGroup.AppAdmin:
            return "Add user permission";
        case AdminRoleAuthGroup.DelegatedAdmin:
            return "Create delegated admin";
        default:
            return "";
    }
};

/**
 * Generates a list of headers based on the authorization group used for skeleton.
 */
export const getHeaders = (authGroup: AdminRoleAuthGroup): string[] => {
    switch (authGroup) {
        case AdminRoleAuthGroup.FamAdmin:
            return [
                "User Name",
                "Domain",
                "Full Name",
                "Email",
                "Application",
                "Environment",
                "Role",
                "Action",
            ];
        case AdminRoleAuthGroup.AppAdmin:
            return [
                "User Name",
                "Domain",
                "Full Name",
                "Email",
                "Role",
                "Action",
            ];
        case AdminRoleAuthGroup.DelegatedAdmin:
            return [
                "User Name",
                "Domain",
                "Full Name",
                "Email",
                "Role Enabled To Assign",
                "Action",
            ];
        default:
            return [];
    }
};

// Allow customized message templates for success and error cases
type NotificationContext<T> = {
    action: string;
    entityName: string;
    successTemplate: (variables: T) => string;
    errorTemplate: (variables: T, error: Error) => string;
};

// For deleteAppAdminMutation
export const deleteAppAdminNotificationContext: NotificationContext<FamApplicationUserRoleAssignmentGetSchema> =
    {
        action: "remove",
        entityName: "access",
        successTemplate: (variables) => `
        You removed ${
            variables.role?.display_name || ""
        } access from ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}
    `,
        errorTemplate: (variables, error) => `
        Failed to remove ${
            variables.role?.display_name || ""
        } access from ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}. Error: ${
            isAxiosError(error) ? formatAxiosError(error) : error.message
        }
    `,
    };

// For deleteDelegatedAdminMutation
export const deleteDelegatedAdminNotificationContext: NotificationContext<FamAccessControlPrivilegeGetResponse> =
    {
        action: "remove",
        entityName: "privilege",
        successTemplate: (variables) => `
        You removed ${
            variables.role?.display_name || ""
        } privilege from ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}
    `,
        errorTemplate: (variables, error) => `
        Failed to remove ${
            variables.role?.display_name || ""
        } privilege from ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}. Error: ${
            isAxiosError(error) ? formatAxiosError(error) : error.message
        }
    `,
    };

// For deleteFamPermissionMutation (different format)
export const deleteFamPermissionNotificationContext: NotificationContext<FamAppAdminGetResponse> =
    {
        action: "remove",
        entityName: "admin privilege",
        successTemplate: (variables) => `
        You removed ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}'s admin privilege for ${
            variables.application.application_description
        }
    `,
        errorTemplate: (variables, error) => `
        Failed to remove ${formatUserNameAndId(
            variables.user.user_name,
            variables.user.first_name,
            variables.user.last_name
        )}'s admin privilege for ${
            variables.application.application_description
        }. Error: ${
            isAxiosError(error) ? formatAxiosError(error) : error.message
        }
    `,
    };

export const createNotification = <T>(
    success: boolean,
    variables: T,
    error: Error | null,
    context: NotificationContext<T>
): PermissionNotificationType => {
    const message = success
        ? context.successTemplate(variables)
        : context.errorTemplate(variables, error as Error);

    return {
        serverity: success ? "success" : "error",
        message,
        hasFullMsg: false,
    };
};

export const NEW_ACCESS_STYLE_IN_TABLE = {
    "background-color": "#C2E0FF",
    "box-shadow": "inset 0 0 0 0.063rem #85C2FF",
};
