import { ref } from 'vue';
import type { FamUserRoleAssignmentCreate } from 'fam-api';

export const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.

export const grantAccessFormData = ref<FamUserRoleAssignmentCreate | null>();

export const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;

export const setGrantAccessFormData = (formData: any) => {
    grantAccessFormData.value = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role_id,
        ...(formData.forestClientNumber
            ? {
                forest_client_number: formData.forestClientNumber.padStart(
                    FOREST_CLIENT_INPUT_MAX_LENGTH,
                    '0'
                ),
            }
            : {}),
    };
}

export const getGrantAccessFormData = () => {
    const data = {
        domain: grantAccessFormData.value?.user_type_code as String,
        userId: grantAccessFormData.value?.user_name as String,
        forestClientNumber:
            grantAccessFormData.value?.forest_client_number as String,
        role_id: grantAccessFormData.value?.role_id as Number | null,
    };
    return data;
}

export const resetGrantAccessFormData = () => {
    grantAccessFormData.value = null;
}