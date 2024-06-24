import { ref } from "vue"
import LoginUserState from '@/store/FamLoginUserState';
import { IdpProvider } from '@/enum/IdpEnum';
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";


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

