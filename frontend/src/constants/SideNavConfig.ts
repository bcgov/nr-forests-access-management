import type { SideNavItemType } from "@/types/SideNavTypes";
import {
    AddAppPermissionRoute,
    AddFamPermissionRoute,
    ManagePermissionsRoute,
    MyPermissionsRoute,
    UserDetailsRoute,
} from "../router/routes";
import UserMultiple from "@carbon/icons-vue/es/user--multiple/16";
import IbmLpa from "@carbon/icons-vue/es/ibm--lpa/16";

export const sideNavItems: SideNavItemType[] = [
    {
        name: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
        icon: UserMultiple,
        subRoutes: [
            AddAppPermissionRoute.name!,
            AddFamPermissionRoute.name!,
            UserDetailsRoute.name!,
        ],
    },
    {
        name: "My permissions",
        routeName: MyPermissionsRoute.name!,
        icon: IbmLpa,
    },
];
