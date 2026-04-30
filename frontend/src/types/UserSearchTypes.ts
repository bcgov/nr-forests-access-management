import { UserType } from "fam-app-acsctl-api/model";

export type UserSearchType = "firstName" | "lastName" | "username";

export interface UserSearchPayload {
    domain: UserType;
    searchType: UserSearchType;
    searchText: string;
}
