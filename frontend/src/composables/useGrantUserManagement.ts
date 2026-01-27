import { ref, computed, readonly, type InjectionKey } from 'vue';
import type { SelectUser } from '@/types/SelectUserType';
import type { IdimProxyBceidInfoSchema, IdimProxyIdirInfoSchema } from 'fam-app-acsctl-api/model';

/**
 * Injection key for grant user management composable.
 */
export const GRANT_USER_MANAGEMENT_KEY = Symbol('grantUserManagement') as InjectionKey<ReturnType<typeof useSelectUserManagement>>;

/**
 * Composable for managing (add/delete) user selection in add regular/admin users permission forms.
 * Supports both multi-user mode (add/remove multiple users) and single-user mode (replace user).
 * Add applicatoin admin, delegated admin flows: use single-user mode.
 * Add regular user flow: uses multi-user mode.
 *
 * @param multiUserMode - If true, allows multiple users; if false, replaces user on add
 * @returns Select user management state and methods
 */
export const useSelectUserManagement = (multiUserMode = false) => {
    const userList = ref<SelectUser[]>([]);

    /**
     * Adds a user to the list.
     * - Multi-user mode: Adds to list if not already present
     * - Single-user mode: Replaces the entire list with new user
     */
    const addUser = (user: SelectUser) => {
        if (!user) return;
        if (multiUserMode) {
            const exists = userList.value.some(
                (u) => u.userId.toLowerCase() === user.userId.toLowerCase()
            );
            if (!exists) {
                userList.value.push(user);
            }
        } else {
            userList.value = [user];
        }
    };

    const deleteUser = (userId: string) => {
        userList.value = userList.value.filter(
            (u) => u.userId.toLowerCase() !== userId.toLowerCase()
        );
    };

    const clearUsers = () => {
        userList.value = [];
    };

    /**
     * Gets the first user (useful for single-user mode).
     */
    const currentUser = computed<SelectUser | null>(
        () => userList.value[0] || null
    );

    const hasUser = (userId: string): boolean => {
        return userList.value.some(
            (u) => u.userId.toLowerCase() === userId.toLowerCase()
        );
    };

    return {
        userList: readonly(userList),
        currentUser,
        multiUserMode,
        addUser,
        deleteUser,
        clearUsers,
        hasUser,
    };
};

/**
 * Converts a backend searched user schema (IDIR or BCeID) to the frontend SelectUser type.
 * @param user - Backend user object (IDIR or BCeID)
 * @returns SelectUser object
 */
export function toSelectUserManagementUser(
  user: IdimProxyBceidInfoSchema | IdimProxyIdirInfoSchema
): SelectUser {
  return {
    userId: user.userId,
    guid: user.guid ?? null,
    firstName: user.firstName ?? null,
    lastName: user.lastName ?? null,
    email: user.email ?? null,
    businessLegalName: (user as any).businessLegalName ?? null,
    businessGuid: (user as any).businessGuid ?? null,
  };
}
