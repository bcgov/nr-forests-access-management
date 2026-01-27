import { ref, computed, readonly, type InjectionKey } from 'vue';
import type { GrantUserManagementUser } from '@/types/GrantUserManagementUser';
import type { IdimProxyBceidInfoSchema, IdimProxyIdirInfoSchema } from 'fam-app-acsctl-api/model';

/**
 * Injection key for provide/inject pattern with type safety.
 */
export const GRANT_USER_MANAGEMENT_KEY = Symbol('grantUserManagement') as InjectionKey<ReturnType<typeof useGrantUserManagement>>;

/**
 * Composable for managing user selection in permission forms.
 * Supports both multi-user mode (add/remove multiple users) and single-user mode (replace user).
 *
 * @param multiUserMode - If true, allows multiple users; if false, replaces user on add
 * @returns User management state and methods
 */
export const useGrantUserManagement = (multiUserMode = false) => {
    const userList = ref<GrantUserManagementUser[]>([]);

    /**
     * Adds a user to the list.
     * - Multi-user mode: Adds to list if not already present
     * - Single-user mode: Replaces the entire list with new user
     */
    const addUser = (user: GrantUserManagementUser) => {
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
    const currentUser = computed<GrantUserManagementUser | null>(
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
 * Converts a backend user schema (IDIR or BCeID) to the frontend GrantUserManagementUser type.
 * @param user - Backend user object (IDIR or BCeID)
 * @returns GrantUserManagementUser object
 */
export function toGrantUserManagementUser(
  user: IdimProxyBceidInfoSchema | IdimProxyIdirInfoSchema
): GrantUserManagementUser {
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
