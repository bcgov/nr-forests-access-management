import { computed, ref } from 'vue';

const termsVisibleState = ref(false);

export const isTermsVisible = computed({
    get: () => termsVisibleState.value,
    set: (value) => {
        termsVisibleState.value = value;
    },
});

export const showTerms = () => {
    termsVisibleState.value = true;
};
