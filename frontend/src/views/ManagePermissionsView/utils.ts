import type { PermissionNotificationType } from "@/types/NotificationTypes";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import type {
    FamAccessControlPrivilegeCreateResponse,
    FamAccessControlPrivilegeResponse,
    FamRoleWithClientDto,
} from "fam-admin-mgmt-api/model";
import type {
    FamRoleWithClientSchema,
    FamUserRoleAssignmentRes,
} from "fam-app-acsctl-api/model";
import { Severity } from "../../types/NotificationTypes";
import type { AppPermissionQueryErrorType } from "../AddAppPermission/utils";

export const generateAppPermissionSuccessNotifications = (
    data: FamUserRoleAssignmentRes | FamAccessControlPrivilegeResponse,
    isDelegatedAdmin: boolean
): PermissionNotificationType[] => {
    const notifications: PermissionNotificationType[] = [];

    /**
     * Represents the status of an email sending operation.
     * TODO: To use new backend multiple user granting but with current application
     *       only one user is granted at a time, so we access the first item's status.
     *       Ticket 2058 will refactor frontend and also address email status handling.
     *
     */
    const emailSendingStatus =
        (data as FamUserRoleAssignmentRes).assignments_detail?.[0]?.email_sending_status ??
        (data as FamAccessControlPrivilegeResponse).email_sending_status;

    const email = data.assignments_detail[0]?.detail.user.email;

    if ("SENT_TO_EMAIL_SERVICE_FAILURE" === emailSendingStatus) {
        notifications.push({
            serverity: Severity.Error,
            message: `
            Failed to send email to ${email}. Contact them and tell them permissions have been granted.`,
            hasFullMsg: false,
        });
    }

    const successRoleList: FamRoleWithClientSchema[] | FamRoleWithClientDto[] =
        (data.assignments_detail as FamAccessControlPrivilegeCreateResponse[])
            .filter((createRes) => createRes.status_code === 200)
            .map((filtered) => filtered.detail.role);

    const successClientList = successRoleList
        .map((role) => role.forest_client)
        .filter((client) => client !== undefined && client !== null);

    const conflictRoleList: FamRoleWithClientSchema[] | FamRoleWithClientDto[] =
        (data.assignments_detail as FamAccessControlPrivilegeCreateResponse[])
            .filter((createRes) => createRes.status_code === 409)
            .map((filtered) => filtered.detail.role);

    const conflictClientList = conflictRoleList
        .map((role) => role.forest_client)
        .filter((client) => client !== undefined && client !== null);

    const famUser = data.assignments_detail[0].detail.user;
    const formattedUserName = formatUserNameAndId(
        famUser.user_name,
        famUser.first_name,
        famUser.last_name
    );

    let actionTerm = isDelegatedAdmin
        ? "granted privilege to manage"
        : "added with";

    // Success notifications for abstract roles
    if (successClientList.length && successRoleList.length) {
        notifications.push({
            serverity: Severity.Success,
            message: `
            ${formattedUserName} was successfully ${actionTerm} organization${
                successClientList.length > 1 ? "s" : ""
            }:
            ${
                successClientList.length > 2
                    ? successClientList
                          .slice(0, 2)
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client?.forest_client_number,
                                  client?.client_name
                              )
                          )
                          .join(", ") +
                      `, and ${successClientList.length - 2} more...`
                    : successClientList
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client?.forest_client_number,
                                  client?.client_name
                              )
                          )
                          .join(", ")
            }
            `,
            hasFullMsg: successClientList.length > 2,
            fullMessage:
                successClientList.length > 2
                    ? `
                        ${formattedUserName} was successfully ${actionTerm} organizations:
                        ${successClientList
                            .map((client) =>
                                formatForestClientDisplayName(
                                    client?.forest_client_number,
                                    client?.client_name
                                )
                            )
                            .join(", ")}
                    `
                    : undefined,
        });
    }
    // Success notifications for concrete roles
    if (!successClientList.length && successRoleList.length) {
        notifications.push({
            serverity: Severity.Success,
            message: `
            ${formattedUserName} was successfully ${actionTerm} the role ${successRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    actionTerm = isDelegatedAdmin
        ? "already has the privilege to manage"
        : "already exists with";

    // Conflict notifications for Abstract roles
    if (conflictClientList.length && conflictRoleList.length) {
        notifications.push({
            serverity: Severity.Error,
            message: `
            ${formattedUserName} ${actionTerm} organization${
                conflictClientList.length > 1 ? "s" : ""
            }:
            ${
                conflictClientList.length > 2
                    ? conflictClientList
                          .slice(0, 2)
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client?.forest_client_number,
                                  client?.client_name
                              )
                          )
                          .join(", ") +
                      `, and ${conflictClientList.length - 2} more...`
                    : conflictClientList
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client?.forest_client_number,
                                  client?.client_name
                              )
                          )
                          .join(", ")
            }
            `,
            hasFullMsg: conflictClientList.length > 2,
            fullMessage:
                conflictClientList.length > 2
                    ? `
                        ${formattedUserName} was successfully ${actionTerm} organizations:
                        ${conflictClientList
                            .map((client) =>
                                formatForestClientDisplayName(
                                    client?.forest_client_number,
                                    client?.client_name
                                )
                            )
                            .join(", ")}
                    `
                    : undefined,
        });
    }

    // Conflict notifications for Concrete roles
    if (!conflictClientList.length && conflictRoleList.length) {
        notifications.push({
            serverity: Severity.Error,
            message: `
            ${formattedUserName} ${actionTerm} the role ${conflictRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    return notifications;
};

export const generateAppPermissionErrorNotifications = (
    errData: AppPermissionQueryErrorType
): PermissionNotificationType => {
    const { user, forestClients, role } = errData.formData;
    const userFullName = formatUserNameAndId(
        user?.userId,
        user?.firstName,
        user?.lastName
    );
    const roleName = role?.display_name;

    return {
        serverity: Severity.Error,
        message: `
        Failed to add ${userFullName} with ${roleName} for organization${
            forestClients.length > 1 ? "s" : ""
        }: ${
            forestClients.length > 2
                ? forestClients
                      .slice(0, 2)
                      .map((client) =>
                          formatForestClientDisplayName(
                              client?.forest_client_number,
                              client?.client_name
                          )
                      )
                      .join(", ") + `, and ${forestClients.length - 2} more...`
                : forestClients
                      .map((client) =>
                          formatForestClientDisplayName(
                              client?.forest_client_number,
                              client?.client_name
                          )
                      )
                      .join(", ")
        }
        `,
        hasFullMsg: forestClients.length > 2,
        fullMessage:
            forestClients.length > 2
                ? `
                   Failed to add ${userFullName} with ${roleName} for organizations:
                    ${forestClients
                        .map((client) =>
                            formatForestClientDisplayName(
                                client?.forest_client_number,
                                client?.client_name
                            )
                        )
                        .join(", ")}
                `
                : undefined,
    };
};

export const generateFamNotification = (
    isSuccess: boolean,
    message: string
): PermissionNotificationType => ({
    serverity: isSuccess ? Severity.Success : Severity.Error,
    message,
    hasFullMsg: false,
});
