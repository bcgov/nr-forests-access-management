import type { SideNavItemType } from "@/types/SideNavTypes";
import { ManagePermissionsRoute, MyPermissionsRoute } from "../router/routes";
import UserMultiple from "@carbon/icons-vue/es/user--multiple/16";
import IbmLpa from "@carbon/icons-vue/es/ibm--lpa/16";
import type { RouteRecordName } from "vue-router";

export const sideNavItems: SideNavItemType[] = [
    {
        name: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
        icon: UserMultiple,
        subRoutes: ManagePermissionsRoute.children?.map(
            (child) => child.name as RouteRecordName
        ),
    },
    {
        name: "My permissions",
        routeName: MyPermissionsRoute.name!,
        icon: IbmLpa,
    },
];
