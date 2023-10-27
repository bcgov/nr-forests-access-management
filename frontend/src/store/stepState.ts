import { ref } from 'vue';
import  type { IconSteps } from '@/enum/IconEnum';

export interface IStepInfo {
    label: string;
    active: boolean;
    icon: IconSteps;
    errorMessage: string;
};

export const stepItems = ref<IStepInfo[]>();