import type {
    AppEnv,
    FamAuthGrantDto,
    FamGrantDetailDto,
    FamRoleDto,
} from "fam-admin-mgmt-api/model";

type MyPermissionsRowType = {
    application: string | null | undefined;
    env: AppEnv | null | undefined;
    role: string;
    clientId?: number;
};

const getFamAdminPermission = (
    access: FamAuthGrantDto
): MyPermissionsRowType[] => {
    const famGrant = access.grants.find(
        (grant: FamGrantDetailDto) => grant.application.id === 1
    );

    if (famGrant) {
        return [
            {
                application: famGrant.application.description,
                env: famGrant.application.env,
                role: "Admin",
            },
        ];
    }
    return [];
};

const getAppAdminPermission = (
    access: FamAuthGrantDto
): MyPermissionsRowType[] => {
    return access.grants.map((grant: FamGrantDetailDto) => ({
        application: grant.application.description,
        env: grant.application.env,
        role: "Admin",
    }));
};

const getDelegatedAdminPermission = (
    access: FamAuthGrantDto
): MyPermissionsRowType[] => {
    const permissions: MyPermissionsRowType[] = [];
    access.grants.forEach((grant: FamGrantDetailDto) => {
        grant.roles?.forEach((role: FamRoleDto) => {
            const roleDescription = "Delegated Admin, " + role.display_name;
            if (!role.forest_clients) {
                permissions.push({
                    application: grant.application.description,
                    env: grant.application.env,
                    role: roleDescription,
                });
            } else {
                role.forest_clients.forEach((clientId: any) => {
                    permissions.push({
                        application: grant.application.description,
                        env: grant.application.env,
                        clientId: clientId,
                        role: roleDescription,
                    });
                });
            }
        });
    });

    return permissions;
};

export const getPermissionTableData = (
    userAccess: FamAuthGrantDto[]
): MyPermissionsRowType[] => {
    let myPermissions: MyPermissionsRowType[] = [];

    userAccess.forEach((access: FamAuthGrantDto) => {
        switch (access.auth_key) {
            case "FAM_ADMIN":
                myPermissions = myPermissions.concat(
                    getFamAdminPermission(access)
                );
                break;
            case "APP_ADMIN":
                myPermissions = myPermissions.concat(
                    getAppAdminPermission(access)
                );
                break;
            case "DELEGATED_ADMIN":
                myPermissions = myPermissions.concat(
                    getDelegatedAdminPermission(access)
                );
                break;
            default:
                break;
        }
    });

    return myPermissions.map((permission) => {
        permission.application = permission
            .application!.replace(/\([^()]*\)/g, "")
            .trim();
        return permission;
    });
};
