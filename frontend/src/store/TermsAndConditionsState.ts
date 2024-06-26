import { ref } from "vue"

export const isTermsVisible = ref(false);

export const isTermsCloseble = ref(false)

export const toggleTermsCloseble = () => {
    isTermsCloseble.value = true
}

export const showTerms = () => {
    isTermsVisible.value = true;
};

export const hideTerms = () => {
    isTermsVisible.value = false;
    isTermsCloseble.value = false;
};

