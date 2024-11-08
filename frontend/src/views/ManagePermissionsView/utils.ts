import type { AddAppPermissionRequestType } from "@/types/RouteTypes";
import type {
    FamAccessControlPrivilegeResponse,
    FamForestClientBase,
    FamRoleWithClientDto,
} from "fam-admin-mgmt-api/model";
import type {
    FamForestClientSchema,
    FamRoleWithClientSchema,
    FamUserRoleAssignmentRes,
} from "fam-app-acsctl-api/model";
import type { PermissionNotificationType } from "@/types/ManagePermissionsTypes";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";

// Define a type guard to check if the role is FamRoleWithClientSchema
function isFamRoleWithClientSchema(
    role: FamRoleWithClientSchema | FamRoleWithClientDto
): role is FamRoleWithClientSchema {
    return (role as FamRoleWithClientSchema).forest_client !== undefined;
}

// success NVADGAMA was successfully granted privilege to manage the role FOM_REVIEWER
// error NVADGAMA already exists with Client ID: 00149081
// OLIBERCH already has the privilege to manage Client ID: 00012797
// success NVADGAMA was successfully added with Client IDs: 00001012, 00012797 and 1 more...
// success OLIBERCH was successfully added with the role FOM_REVIEWER
// success OLIBERCH was successfully granted privilege to manage Client IDs: 00149081, 00001012 and 2 more... See all
export const generateAppSuccessNotifications = (
    requestType: AddAppPermissionRequestType,
    data: FamUserRoleAssignmentRes | FamAccessControlPrivilegeResponse
): PermissionNotificationType[] => {
    const notifications: PermissionNotificationType[] = [];

    const email = data.assignments_detail[0]?.detail.user.email;

    if (data.email_sending_status === "SENT_TO_EMAIL_SERVICE_FAILURE") {
        notifications.push({
            serverity: "error",
            message: `
            Failed to send email to ${email}. Contact them and tell them permissions have been granted.`,
            hasFullMsg: false,
        });
    }

    const successRoleList: FamRoleWithClientSchema[] | FamRoleWithClientDto[] =
        data.assignments_detail
            .filter((createRes) => createRes.status_code === 200)
            .map((filtered) => filtered.detail.role);

    const successClientList: FamForestClientSchema[] | FamForestClientBase[] =
        successRoleList
            .map((role) =>
                isFamRoleWithClientSchema(role)
                    ? role.forest_client
                    : role.client_number
            )
            .filter((client) => client !== undefined && client !== null);

    const conflictRoleList: FamRoleWithClientSchema[] | FamRoleWithClientDto[] =
        data.assignments_detail
            .filter((createRes) => createRes.status_code === 409)
            .map((filtered) => filtered.detail.role);

    const conflictClientList: FamForestClientSchema[] | FamForestClientBase[] =
        conflictRoleList
            .map((role) =>
                isFamRoleWithClientSchema(role)
                    ? role.forest_client
                    : role.client_number
            )
            .filter((client) => client !== undefined && client !== null);

    const famUser = data.assignments_detail[0].detail.user;
    const formattedUserName = formatUserNameAndId(
        famUser.user_name,
        famUser.first_name,
        famUser.last_name
    );

    let actionTerm =
        requestType === "addUserPermission"
            ? "added with"
            : "granted privilege to manage";

    // Success notifications for abstract roles
    if (successClientList.length && successRoleList.length) {
        notifications.push({
            serverity: "success",
            message: `
            ${formattedUserName} was successfully ${actionTerm} Organization${
                successClientList.length > 1 ? "s" : ""
            }:
            ${
                successClientList.length > 2
                    ? successClientList
                          .slice(0, 2)
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client.forest_client_number,
                                  client.client_name
                              )
                          )
                          .join(", ") +
                      `, and ${successClientList.length - 2} more...`
                    : successClientList
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client.forest_client_number,
                                  client.client_name
                              )
                          )
                          .join(", ")
            }
            `,
            hasFullMsg: successClientList.length > 2,
            fullMessage:
                successClientList.length > 2
                    ? `
                        ${formattedUserName} was successfully ${actionTerm} Organizations:
                        ${successClientList
                            .map((client) =>
                                formatForestClientDisplayName(
                                    client.forest_client_number,
                                    client.client_name
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
            serverity: "success",
            message: `
            ${formattedUserName} was successfully ${actionTerm} the role ${successRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    actionTerm =
        requestType === "addUserPermission"
            ? "already exists with"
            : "already has the privilege to manage";

    // Conflict notifications for Abstract roles
    if (conflictClientList.length && conflictRoleList.length) {
        notifications.push({
            serverity: "error",
            message: `
            ${formattedUserName} ${actionTerm} Organization${
                conflictClientList.length > 1 ? "s" : ""
            }:
            ${
                conflictClientList.length > 2
                    ? conflictClientList
                          .slice(0, 2)
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client.forest_client_number,
                                  client.client_name
                              )
                          )
                          .join(", ") +
                      `, and ${conflictClientList.length - 2} more...`
                    : conflictClientList
                          .map((client) =>
                              formatForestClientDisplayName(
                                  client.forest_client_number,
                                  client.client_name
                              )
                          )
                          .join(", ")
            }
            `,
            hasFullMsg: conflictClientList.length > 2,
            fullMessage:
                conflictClientList.length > 2
                    ? `
                        ${formattedUserName} was successfully ${actionTerm} Organizations:
                        ${conflictClientList
                            .map((client) =>
                                formatForestClientDisplayName(
                                    client.forest_client_number,
                                    client.client_name
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
            serverity: "error",
            message: `
            ${formattedUserName} ${actionTerm} the role ${conflictRoleList[0].display_name}
            `,
            hasFullMsg: false,
        });
    }

    return notifications;
};
