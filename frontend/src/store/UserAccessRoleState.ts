import ApiServiceFactory from "@/services/ApiServiceFactory";
import { requireInjection } from "@/services/utils";
import type { FamApplicationUserRoleAssignmentGet } from "fam-app-acsctl-api";
import { shallowRef } from "vue";

export const userRoleAssignments = shallowRef<FamApplicationUserRoleAssignmentGet[]>([]);

// --- Setter

export const setUserRoleAssignments = (newValue: FamApplicationUserRoleAssignmentGet[]) => {
    userRoleAssignments.value = newValue;
}

// --- Fetching (backend)

export const fetchUserRoleAssignments = async (applicationId: number | undefined) => {
    if (!applicationId) return;

    // TODO: find a way to refactor this "requireInjection" only for vue component and won't work properly here.
    const appActlApiService = requireInjection(ApiServiceFactory.APP_ACCESS_CONTROL_API_SERVICE_KEY);
    const userRoleAssignments = (
        await appActlApiService
            .applicationsApi.getFamApplicationUserRoleAssignment(applicationId)
    ).data;

    // sorting
    userRoleAssignments.sort((first, second) => {
        // by user_name
        const userNameCompare = first.user.user_name.localeCompare(
            second.user.user_name
        );
        const roleNameCompare = first.role.role_name.localeCompare(
            second.role.role_name
        );
        return (userNameCompare != 0)? userNameCompare: roleNameCompare;
    });
    setUserRoleAssignments(userRoleAssignments);
};