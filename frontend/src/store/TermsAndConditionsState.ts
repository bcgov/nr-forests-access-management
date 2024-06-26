import { computed, ref } from 'vue';

const termsVisibleState = ref(false);
const termsClosableState = ref(false);

export const isTermsVisible = computed({
    get: () => termsVisibleState.value,
    set: (value) => {
        termsVisibleState.value = value;
    },
});

export const isTermsClosable = computed({
    get: () => termsClosableState.value,
    set: (value) => {
        termsClosableState.value = value;
    },
});

export const toggleTermsCloseble = () => {
    termsClosableState.value = true;
};

export const showTerms = () => {
    termsVisibleState.value = true;
};

export const hideTerms = () => {
    termsVisibleState.value = false;
    termsClosableState.value = false;
};
