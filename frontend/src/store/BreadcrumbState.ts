import { ref } from 'vue';
import type { IRouteInfo } from '@/router';

export const breadcrumbState = ref();

export const populateBreadcrumb = (breadcrumbItem: IRouteInfo[]) => {
    breadcrumbState.value = breadcrumbItem;
};