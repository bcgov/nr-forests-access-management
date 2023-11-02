import { ref } from 'vue';
import  type { IconSteps } from '@/enum/IconEnum';

export interface IStepInfo {
    label: string;
    active: boolean;
    icon: IconSteps;
    errorMessage: string;
};

export const stepItems = ref<IStepInfo[]>();

export const setStepItems = (newStepItemsValue: IStepInfo[]) => {
    stepItems.value = newStepItemsValue;
}

export const addNewStep = (newStep: IStepInfo) => {
    stepItems.value?.push(newStep)
}