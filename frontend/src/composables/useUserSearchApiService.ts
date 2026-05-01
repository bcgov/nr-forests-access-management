import { AppActlApiService } from "@/services/ApiServiceFactory";
import type { SelectedUser } from "@/types/SelectUserType";
import type { UserSearchParams } from "@/types/UserSearchTypes";
import { useMutation } from "@tanstack/vue-query";
import type {
    IdimProxyBceidInfoSchema,
    IdimProxyIdirUserSearchItemResSchema,
} from "fam-app-acsctl-api";
import { UserType } from "fam-app-acsctl-api/model";
import { ref } from "vue";

/**
 * Composable/service that provides user search functionality using the IDIM-Proxy IDIR/BCeID API.
 * This encapsulates the API call logic, normalization of results, and error handling for user searches
 * with tanstack/vue-query useMutation.
 */

const IDIR_SEARCH_PAGE_SIZE = 250;

function normalizeIdirItem(
    item: IdimProxyIdirUserSearchItemResSchema
): SelectedUser {
    const firstName = item.firstName ?? "";
    const lastName = item.lastName ?? "";
    return {
        userId: item.userId,
        guid: item.guid ?? null,
        firstName,
        lastName,
        email: item.email ?? "",
        fullName: [firstName, lastName].filter(Boolean).join(" "),
        sourceDomain: UserType.I,
    };
}

function normalizeBceidItem(item: IdimProxyBceidInfoSchema): SelectedUser {
    const firstName = item.firstName ?? "";
    const lastName = item.lastName ?? "";
    return {
        userId: item.userId,
        guid: item.guid ?? null,
        firstName,
        lastName,
        email: item.email ?? "",
        fullName: [firstName, lastName].filter(Boolean).join(" "),
        sourceDomain: UserType.B,
    };
}

export function useUserSearchApiService() {
    const searchError = ref<string | null>(null);

    const searchMutation = useMutation({
        retry: 1,
        mutationFn: async (params: UserSearchParams): Promise<SelectedUser[]> => {
            if (params.domain === UserType.I) {
                const firstName =
                    params.searchType === "firstName" ? params.searchText : undefined;
                const lastName =
                    params.searchType === "lastName" ? params.searchText : undefined;
                const userId =
                    params.searchType === "username" ? params.searchText : undefined;

                const res = await AppActlApiService.idirBceidProxyApi.searchIdirUsers(
                    params.appId,
                    firstName,
                    lastName,
                    userId,
                    IDIR_SEARCH_PAGE_SIZE,
                    // 20 seconds timeout for IDIM/IDIR search, broader search with heavy load can be slow.
                    // This overrides the default 10 seconds timeout set in ApiServiceFactory for this specific API call only.
                    {timeout: 20000}
                );
                return res.data.items.map(normalizeIdirItem);
            } else {
                const res = await AppActlApiService.idirBceidProxyApi.bceidLookup(
                    params.searchText,
                    params.appId
                );
                if (!res.data.found) {
                    return [];
                }
                return [normalizeBceidItem(res.data)];
            }
        },
        onError: (error: unknown) => {
            console.error("User search failed:", error);
            searchError.value =
                "Search failed. Please try again or contact support if the issue persists.";
        },
        onSuccess: () => {
            searchError.value = null;
        },
    });

    const searchUsers = (params: UserSearchParams) => {
        searchMutation.reset();
        searchError.value = null;
        searchMutation.mutate(params);
    };

    return {
        searchUsers,
        isPending: searchMutation.isPending,
        searchResults: searchMutation.data,
        isSuccess: searchMutation.isSuccess,
        searchError,
        reset: () => {
            searchMutation.reset();
            searchError.value = null;
        },
    };
}
