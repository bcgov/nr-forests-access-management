import { UserType } from "fam-app-acsctl-api/model";

export type UserSearchType = "firstName" | "lastName" | "username";

export interface UserSearchPayload {
    domain: UserType;
    searchType: UserSearchType;
    searchText: string;
}

export interface UserSearchResultRow {
    userId: string;
    guid: string | null;
    firstName: string | null;
    lastName: string | null;
    email: string | null;
    fullName: string;
    sourceDomain: UserType;
}

export interface UserSearchParams {
    domain: UserType;
    searchType: UserSearchType;
    searchText: string;
    appId: number;
}
