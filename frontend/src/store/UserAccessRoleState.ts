import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import { shallowRef } from 'vue';

export const userRoleAssignments = shallowRef<
    FamApplicationUserRoleAssignmentGet[]
>([]);

// --- Setter

export const setUserRoleAssignments = (
    newValue: FamApplicationUserRoleAssignmentGet[]
) => {
    userRoleAssignments.value = newValue;
};
