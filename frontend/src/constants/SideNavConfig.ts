import type { SideNavItemType } from "@/types/SideNavTypes";
import UserMultiple from "@carbon/icons-vue/es/user--multiple/16";
import IbmLpa from "@carbon/icons-vue/es/ibm--lpa/16";

export const sideNavItems: SideNavItemType[] = [
    {
        name: "Manage permissions",
        link: "/manage-permissions",
        icon: UserMultiple,
        childLinks: [
            "/user-details",
            "/grant",
            "/grant-app-admin",
            "/grant-delegated-admin",
        ],
    },
    {
        name: "My permissions",
        link: "/my-permissions",
        icon: IbmLpa,
        disabled: false,
    },
];
