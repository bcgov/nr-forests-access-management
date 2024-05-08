import { ref } from 'vue';

const currentTabState = ref<string>("");

export const setCurrentTabState = (status: string) => {
    currentTabState.value = status;
}

export const getCurrentTabState = (): string => {
    return currentTabState.value;
}