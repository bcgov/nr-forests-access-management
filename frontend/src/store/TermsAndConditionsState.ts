import { ref } from 'vue';

export const isTermsVisible = ref(false);
export const isTermsCloseable = ref(false);

export const showTermsForAcceptance = () => {
    isTermsVisible.value = true;
    isTermsCloseable.value = false;
};

export const hideTerms = () => {
    isTermsVisible.value = false;
};

export const showTermsForRead = () => {
    isTermsVisible.value = true;
    isTermsCloseable.value = true;
};
