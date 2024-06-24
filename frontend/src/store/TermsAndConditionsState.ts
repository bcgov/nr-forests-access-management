import { ref } from "vue"

export const isTermsVisible = ref(false);

export const isAbleToClose = ref(false)

export const toggleCloseble = () => {
    isAbleToClose.value = true
}

export const showTerms = () => {
    isTermsVisible.value = true;
};

export const hideTerms = () => {
    isTermsVisible.value = false;
    isAbleToClose.value = false;
};

