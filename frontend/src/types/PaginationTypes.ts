import type {
    SortOrderEnum,
    UserRoleSortByEnum,
} from "fam-app-acsctl-api/model";

export type PaginationType = {
    pageNumber: number;
    pageSize: number;
    search: string | null;
    sortOrder: SortOrderEnum | null;
    sortBy: UserRoleSortByEnum | null;
};
