import type { AxiosError } from "axios";
import type {
    AdminUserAccessResponse,
    FamApplicationDto,
} from "fam-admin-mgmt-api/model";

/**
 * Formats an Axios error into a string containing the status and error message.
 *
 * @param {AxiosError} err - The Axios error object.
 * @returns {string} A formatted error string in the format "status: message".
 */
export const formatAxiosError = (err: AxiosError): string =>
    `${err.response?.status}: ${err.message}`;

/**
 * Extracts unique applications from the AdminUserAccessResponse.
 *
 * @param {AdminUserAccessResponse} data - The response containing user access information.
 * @returns {FamApplicationDto[]} An array of unique FamApplicationDto objects.
 */
export const getUniqueApplications = (
    data?: AdminUserAccessResponse
): FamApplicationDto[] => {
    if (!data) {
        return [];
    }
    return Array.from(
        data.access
            .flatMap((authGrant) =>
                authGrant.grants.map((grant) => grant.application)
            )
            .reduce((acc, app) => acc.set(app.id, app), new Map())
            .values()
    );
};
