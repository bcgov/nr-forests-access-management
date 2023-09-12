import { toRaw, ref } from 'vue';
import authService from '@/services/AuthService';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';

import {
    domainOptions,
    getGrantAccessFormData,
    grantAccessFormData,
    resetGrantAccessFormData,
} from '@/store/GrantAccessDataState';

import { selectedApplication } from '@/store/ApplicationState';

import type { FamApplicationRole } from 'fam-api';

let applicationRoleOptions: FamApplicationRole[];
const loadingData = ref(false);
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const roles = toRaw(authService.state.value.famLoginUser!.roles);
console.log(roles);

const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumber: '',
    role_id: null as number | null,
};

const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input

function resetForm() {
    resetGrantAccessFormData();
    formData.value = defaultFormData;
}

const getApplicationRoles = async (to, from, next) => {
    //setTimeout just to show explicitly that the guard is waiting
    setTimeout(async () => {
        try {
            applicationRoleOptions = (
                await applicationsApi.getFamApplicationRoles(
                    selectedApplication.value?.application_id as number
                )
            ).data;

            if (grantAccessFormData.value) {
                formData.value = getGrantAccessFormData();
            } else {
                resetForm();
            }
        } catch (error: unknown) {
            return Promise.reject(error);
        } finally {
            console.log(loadingData.value);
            next();
        }
    }, 3000);
};

export { getApplicationRoles, resetForm, applicationRoleOptions, loadingData };
