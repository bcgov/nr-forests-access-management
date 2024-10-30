import { UserType } from "fam-app-acsctl-api/model";

export type AppPermissionFormType = {
    domain: UserType;
    userId: string;
    userGuid: string;
    forestClientIds: string[];
    roleId: number | null;
    sendUserEmail: boolean;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    userId: "",
    userGuid: "",
    forestClientIds: [],
    roleId: null,
    sendUserEmail: false,
};

export const getDefaultFormData = (
    domain: UserType,
    sendUserEmail: boolean
): AppPermissionFormType => {
    const copy = structuredClone(defaultFormData);
    return {
        ...copy,
        domain,
        sendUserEmail,
    };
};
