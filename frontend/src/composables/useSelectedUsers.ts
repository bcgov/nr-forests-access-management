import { ref, computed, readonly, type InjectionKey } from 'vue';
import type { SelectedUser } from '@/types/SelectUserType';
import type { IdimProxyBceidInfoSchema, IdimProxyIdirInfoSchema } from 'fam-app-acsctl-api/model';

/**
 * Injection key for selected users composable.
 */
export const ADD_PERMISSION_SELECT_USER_KEY = Symbol('addPermissionSelectUser') as InjectionKey<ReturnType<typeof useSelectedUsers>>;

/**
 * Composable for managing (add/delete) user selection in add regular/admin users permission forms.
 * Supports both multi-user mode (add/remove multiple users) and single-user mode (replace user).
 * Add application admin, delegated admin flows: use single-user mode.
 * Add regular user flow: uses multi-user mode.
 *
 * @param multiUserMode - If true, allows multiple users; if false, replaces user on add
 * @returns Selected users state and methods
 */
export const useSelectedUsers = (multiUserMode = false) => {
    const userList = ref<SelectedUser[]>([]);

    /**
     * Adds a user to the list.
     * - Multi-user mode: Adds to list if not already present
     * - Single-user mode: Replaces the entire list with new user
     */
    const addUser = (user: SelectedUser) => {
        if (!user) return;
        if (multiUserMode) {
            const exists = hasUser(user.userId, user.guid ?? undefined);
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
    const currentUser = computed<SelectedUser | null>(
        () => userList.value[0] || null
    );

    /**
     * Utility to check if a user exists in a user list by userId (case-insensitive).
     * @param userId - User ID to check
     * @param guid - Optional GUID to check
     * @returns true if user exists, false otherwise
     */
    const hasUser = (userId: string, guid?: string): boolean => {
        return userList.value.some((u) => {
            const userIdMatch = u.userId.toLowerCase() === userId.toLowerCase();
            const guidMatch = guid ? (u.guid?.toLowerCase() === guid.toLowerCase()) : true;
            return userIdMatch && guidMatch;
        });
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
 * Converts a backend searched user schema (IDIR or BCeID) to the frontend SelectedUser type.
 * @param user - Backend user object (IDIR or BCeID)
 * @returns SelectedUser object
 */
export function toSelectedUser(
  user: IdimProxyBceidInfoSchema | IdimProxyIdirInfoSchema
): SelectedUser {
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
