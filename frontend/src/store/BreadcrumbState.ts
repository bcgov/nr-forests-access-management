import type { IRouteInfo } from "@/router/RouteItem";
import { ref } from "vue";

export const breadcrumbState = ref();

// This is a special item to fit the limitation of "PrimeVue" Breadcrum that
// the very last item for breadcrum is not rendering as a link. It will be append
// at the end of the `breadcrumbItem` array
const crumbEndItem = {
    name: "endCrumb",
    path: "", // deliberately empty.
    label: undefined, // deliberately undefined.
};

/**
 * 'breadcrumbItem' items to display for current routed component.
 * Note:
 * - We don't need to show the current page crumb item.
 * - PrmeVue has limitation that the last crumb item will not be rendered as a link.
 *   So `crumbEndItem` is always appended at the end to make first item always is
 *   a link for convenience.
 * @param breadcrumbItem
 */
export const populateBreadcrumb = (breadcrumbItem: IRouteInfo[]) => {
    breadcrumbItem.push(crumbEndItem);
    breadcrumbState.value = breadcrumbItem;
};
