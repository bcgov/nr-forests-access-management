import FailedGrantAppUsersNtfnTemplate from "@/components/NotificationContent/FailedGrantAppUsersNtfnTemplate.vue";
import SccssGrantAppUsersNtfnTemplate from "@/components/NotificationContent/SccssGrantAppUsersNtfnTemplate.vue";
import type { PermissionNotificationType } from "@/types/NotificationTypes";
import { Severity } from "@/types/NotificationTypes";
import { mapAppUserGrantResponseByUserId } from "@/utils/ApiUtils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { AddAppUserPermissionErrorQuerykey, AddAppUserPermissionSuccessQuerykey, AddDelegatedAdminErrorQuerykey, AddDelegatedAdminSuccessQuerykey, type AppPermissionQueryErrorType } from "@/views/AddAppPermission/utils";
import type { QueryClient } from "@tanstack/vue-query";
import type {
    FamAccessControlPrivilegeCreateResponse,
    FamAccessControlPrivilegeResponse,
    FamRoleWithClientDto,
} from "fam-admin-mgmt-api/model";
import {
    EmailSendingStatus,
    type FamRoleWithClientSchema,
    type FamUserRoleAssignmentRes
} from "fam-app-acsctl-api/model";
import { h, type Ref } from "vue";
import { AddAppAdminErrorQueryKey, AddAppAdminSuccessQueryKey } from "../AddFamPermission/utils";

export const toAppUserGrantPermissionNotification = (
    data: FamUserRoleAssignmentRes | null,
    applicationName: string | null
): PermissionNotificationType[] => {
    if (!data || data.assignments_detail.length === 0) {
        return [];
    }

    // success case: grouped by user ID and use first result per user for success notification
    const successAssignmentsByUser = Array.from(
        mapAppUserGrantResponseByUserId(
            data.assignments_detail.filter((assignment) => assignment.status_code === 200)
        ).values()
    ).map((items) => items[0]);

    // failure case: grouped by user ID and use first result per user for error notification
    const failedOrEmailSendingErrorAssignments = data.assignments_detail.filter(
        (assignment) =>
            assignment.status_code !== 200 || assignment.email_sending_status === EmailSendingStatus.SentToEmailServiceFailure
    );

    const notifications: PermissionNotificationType[] = [];
    if (successAssignmentsByUser.length > 0) {
        notifications.push({
            severity: Severity.Success,
            message: h(SccssGrantAppUsersNtfnTemplate, {
                assignments: successAssignmentsByUser,
                applicationName,
            }),
            hasFullMsg: false
        });
    }
    if (failedOrEmailSendingErrorAssignments.length > 0) {
        notifications.push({
            severity: Severity.Error,
            message: h(FailedGrantAppUsersNtfnTemplate, {
                assignments: failedOrEmailSendingErrorAssignments,
                applicationName,
            }),
            hasFullMsg: false
        });
    }
    return notifications;
};

export const toAppUserGrantReqErrorNotification = (
    errData: AppPermissionQueryErrorType | null,
    applicationName: string | null,
): PermissionNotificationType[] => {
    console
    if (!errData) {
        return [];
    }

    return [{
        severity: Severity.Error,
        message: h(FailedGrantAppUsersNtfnTemplate, {
            applicationName: applicationName,
            requestErrorData:errData
        }),
        hasFullMsg: false
    }];
};

export const toDelegatedAdminGrantSuccessNotification = (
    data: FamAccessControlPrivilegeResponse
): PermissionNotificationType[] => {
    const notifications: PermissionNotificationType[] = [];
    const emailSendingStatus = data.email_sending_status;
    const email = data.assignments_detail[0]?.detail.user.email;

    if ("SENT_TO_EMAIL_SERVICE_FAILURE" === emailSendingStatus) {
        notifications.push({
            severity: Severity.Error,
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

    let actionTerm = "granted privilege to manage";

    // Success notifications for abstract roles
    if (successClientList.length && successRoleList.length) {
        notifications.push({
            severity: Severity.Success,
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
            severity: Severity.Success,
            message: `
            ${formattedUserName} was successfully ${actionTerm} the role ${successRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    actionTerm = "already has the privilege to manage";

    // Conflict notifications for Abstract roles
    if (conflictClientList.length && conflictRoleList.length) {
        notifications.push({
            severity: Severity.Error,
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
            severity: Severity.Error,
            message: `
            ${formattedUserName} ${actionTerm} the role ${conflictRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    return notifications;
};

export const toDelegatedAdminGrantReqErrorNotifications = (
    errData: AppPermissionQueryErrorType
): PermissionNotificationType => {
    const { users, forestClients, role } = errData.formData;
    // For delegated admin, only one user is available in the form data 'users' array
    const userFullName = formatUserNameAndId(
        users[0].userId,
        users[0].firstName,
        users[0].lastName
    );
    const roleName = role?.display_name;

    return {
        severity: Severity.Error,
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
    severity: isSuccess ? Severity.Success : Severity.Error,
    message,
    hasFullMsg: false,
});

export const clearNotifications = (queryClient: QueryClient, notifications: Ref<PermissionNotificationType[]>) => {
    queryClient.removeQueries({
        queryKey: [AddAppUserPermissionSuccessQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddAppUserPermissionErrorQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddDelegatedAdminSuccessQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddDelegatedAdminErrorQuerykey],
    });
    queryClient.removeQueries({
        queryKey: [AddAppAdminSuccessQueryKey],
    });
    queryClient.removeQueries({
        queryKey: [AddAppAdminErrorQueryKey],
    });
    notifications.value = [];
};