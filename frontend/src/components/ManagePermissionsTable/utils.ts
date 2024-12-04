import { ManagePermissionsTableEnum } from "@/types/ManagePermissionsTypes";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import { Severity } from "@/types/NotificationTypes";
import { formatAxiosError } from "@/utils/ApiUtils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { isAxiosError } from "axios";
import {
    type FamAccessControlPrivilegeGetResponse,
    type FamAppAdminGetResponse,
} from "fam-admin-mgmt-api/model";
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
    "create_date",
];

/**
 * Generates the header title text for the table based on the application name.
 */
export const getTableHeaderTitle = (
    appName: string,
    tableType: ManagePermissionsTableEnum
): string => {
    switch (tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return `${appName} users`;
        case ManagePermissionsTableEnum.AppUser:
            return `${appName} users`;
        case ManagePermissionsTableEnum.DelegatedAdmin:
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
    tableType: ManagePermissionsTableEnum
): string => {
    switch (tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case ManagePermissionsTableEnum.AppUser:
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return `
            This table shows all the delegated administrators in ${appName} and the roles they are allowed to manage for their users
            `;
        default:
            return `This table shows all the users in ${appName} and their permissions levels`;
    }
};

/**
 * Generates a list of headers based on the authorization group used for skeleton.
 */
export const getHeaders = (tableType: ManagePermissionsTableEnum): string[] => {
    switch (tableType) {
        case ManagePermissionsTableEnum.AppAdmin:
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
        case ManagePermissionsTableEnum.AppUser:
            return [
                "User Name",
                "Domain",
                "Full Name",
                "Email",
                "Role",
                "Added On",
                "Action",
            ];
        case ManagePermissionsTableEnum.DelegatedAdmin:
            return [
                "User Name",
                "Domain",
                "Full Name",
                "Email",
                "Role Enabled To Assign",
                "Added On",
                "Action",
            ];
        default:
            return [];
    }
};

/**
 * Defines a customizable context for generating notifications with success and error message templates.
 *
 * @template T - The shape of the `variables` object passed to the templates, allowing flexible
 * substitution of values within the message strings.
 *
 * @property {string} action - Action type for the notification, e.g., "add", "remove".
 * @property {string} entityName - The name of the entity affected, e.g., "access", "privilege".
 * @property {function(T): string} successTemplate - A template function that generates the success message.
 * @property {function(T, Error): string} errorTemplate - A template function that generates the error message.
 */

type NotificationContext<T> = {
    action: string;
    entityName: string;
    successTemplate: (variables: T) => string;
    errorTemplate: (variables: T, error: Error) => string;
};

// For deleteAppUserRoleMutation
export const deleteAppUserRoleNotificationContext: NotificationContext<FamApplicationUserRoleAssignmentGetSchema> =
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

/**
 * Creates a notification message based on the operation's success or failure.
 *
 * @template T - The shape of the `variables` object passed to the templates. This generic type allows
 * `createNotification` to accept various structures for `variables`, ensuring flexibility and type safety
 * across different types of notification contexts.
 *
 * Possible types for `T`:
 *  - `FamApplicationUserRoleAssignmentGetSchema`: For App user role assignment notifications.
 *  - `FamAccessControlPrivilegeGetResponse`: For Delegated Admin notifications.
 *  - `FamAppAdminGetResponse`: For FAM App Admin privilege notifications.
 *
 * @param {boolean} success - Indicates whether the operation was successful.
 * @param {T} variables - Variables used to customize the success or error message template.
 * @param {Error | null} error - The error object to pass to the error template if the operation failed.
 * @param {NotificationContext<T>} context - The context defining the message templates and entity details.
 * @returns {PermissionNotificationType} - An object representing the notification to be displayed.
 */
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
        serverity: success ? Severity.Success : Severity.Error,
        message,
        hasFullMsg: false,
    };
};

export const NEW_ACCESS_STYLE_IN_TABLE = {
    "background-color": "#C2E0FF",
    "box-shadow": "inset 0 0 0 0.063rem #85C2FF",
};

/**
 * DataTable 'Organization' column display expression.
 * @param {ManagePermissionsTableEnum} tableType - ManagePermissionsTable table types.
 * @param {FamApplicationUserRoleAssignmentGetSchema | FamAccessControlPrivilegeGetResponse} data - provided
 *        datatable data to extract and format forest client information for the 'Organization' column. Only
 *        user table and delegated admin table have this column.
 */
export const displayForestClient = (
    tableType: ManagePermissionsTableEnum,
    data:
        | FamApplicationUserRoleAssignmentGetSchema
        | FamAccessControlPrivilegeGetResponse
) => {
    const forestClientData = data.role.forest_client;
    if (tableType === ManagePermissionsTableEnum.AppUser) {
        // Display formatted forest client display name.
        return forestClientData
            ? formatForestClientDisplayName(
                  forestClientData.forest_client_number,
                  forestClientData.client_name
              )
            : "";
    } else {
        // For delegated admin data.
        // TODO: No client name available from backend yet, implement soon. Only display client number. # noqa NOSONAR
        return forestClientData?.forest_client_number;
    }
};
