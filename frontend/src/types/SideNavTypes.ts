import type { Component } from "vue";

/**
 * Type definition for a side navigation item.
 *
 * @property {string} name - The display name of the navigation item.
 * @property {string} link - The base URL or route for the navigation item.
 * @property {string} [icon] - Optional. The icon import from @carbon/icons-vue,
 *                             example: require("@carbon/icons-vue/es/user--multiple/16"
 * @property {SideNavItemType[]} [subMenuItems] - Optional array of submenu items.
 *                                                Each submenu item follows the same structure as `SideNavItemType`,
 *                                                allowing for nested navigation.
 * @property {string[]} childLinks - Optional array of sub-routes. If the current URL matches any sub-route
 *                                     (e.g., `link` is `/a/` and a sub-route is `/a/apple`),
 *                                     the parent link (`/a/`) will be considered active.
 * @property {boolean} [disabled=false] - Optional flag to disable the navigation item. Default is false.
 */
export type SideNavItemType = {
    name: string;
    link: string;
    icon?: Component;
    subMenuItems?: SideNavItemType[];
    childLinks?: string[];
    disabled?: boolean;
};
