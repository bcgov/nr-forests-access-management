import { ref } from 'vue';
export interface IBreadcrumbItem {
    label: string,
    to: string
};

export type Breadcrumb = {
    [key: string]: IBreadcrumbItem
};

export const breadcrumbState = ref();

export const populateBreadcrumb = (breadcrumbItem: IBreadcrumbItem[]) => {
    breadcrumbState.value = breadcrumbItem;
};