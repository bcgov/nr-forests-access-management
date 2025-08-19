import {
    AdminRoleAuthGroup,
    type AppEnv,
    type FamAuthGrantDto,
    type FamGrantDetailDto,
    type FamRoleGrantDto,
} from "fam-admin-mgmt-api/model";

type MyPermissionsRowType = {
    application: string | null | undefined;
    env: AppEnv | null | undefined;
    role: string;
    forestClient?: string;
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
                role: "Application Admin",
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
        role: "Application Admin",
    }));
};

const getDelegatedAdminPermission = (
    access: FamAuthGrantDto
): MyPermissionsRowType[] => {
    const permissions: MyPermissionsRowType[] = [];
    access.grants.forEach((grant: FamGrantDetailDto) => {
        grant.roles?.forEach((role: FamRoleGrantDto) => {
            const roleDescription = "Delegated Admin, " + role.display_name;
            if (!role.forest_clients) {
                permissions.push({
                    application: grant.application.description,
                    env: grant.application.env,
                    role: roleDescription,
                });
            } else {
                role.forest_clients.forEach((forestClient) => {
                    permissions.push({
                        application: grant.application.description,
                        env: grant.application.env,
                        forestClient: `${forestClient.forest_client_number} ${forestClient.client_name}`,
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
            case AdminRoleAuthGroup.FamAdmin:
                myPermissions = myPermissions.concat(
                    getFamAdminPermission(access)
                );
                break;
            case AdminRoleAuthGroup.AppAdmin:
                myPermissions = myPermissions.concat(
                    getAppAdminPermission(access)
                );
                break;
            case AdminRoleAuthGroup.DelegatedAdmin:
                myPermissions = myPermissions.concat(
                    getDelegatedAdminPermission(access)
                );
                break;
            default:
                break;
        }
    });

    // Remove any text within parentheses (e.g., "FOM (DEV)" -> "FOM ") , including the parentheses themselves,
    // from the `application` string, then trim any extra whitespace.
    return myPermissions.map((permission) => {
        permission.application = permission.application
            ?.replace(/\([^()]*\)/g, "")
            .trim();
        return permission;
    });
};
