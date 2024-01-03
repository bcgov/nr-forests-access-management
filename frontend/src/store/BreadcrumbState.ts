import type { IRouteInfo } from '@/router/routeItem';
import { ref } from 'vue';

export const breadcrumbState = ref();

export const populateBreadcrumb = (breadcrumbItem: IRouteInfo[]) => {
    breadcrumbState.value = breadcrumbItem;
};