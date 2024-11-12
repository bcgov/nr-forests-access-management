import type {
    FamAppAdminCreateRequest,
    FamApplicationDto,
} from "fam-admin-mgmt-api/model";
import { UserType } from "fam-app-acsctl-api";
import type { IdimProxyIdirInfoSchema } from "fam-app-acsctl-api/model";
import { mixed, object } from "yup";

export const FamPermissionSuccessQueryKey = "fam-permission-success";
export const FamPermissionErrorQueryKey = "fam-permission-error";

export const NewFamAdminQueryParamKey = "newFamAdminIds";

export type FamPermissionFormType = {
    user: IdimProxyIdirInfoSchema | null;
    application: FamApplicationDto | null;
};

const defaultFormData: FamPermissionFormType = {
    user: null,
    application: null,
};

export const getDefaultFormData = (): FamPermissionFormType =>
    structuredClone(defaultFormData);

/**
 * Validation schema for fam admin
 */
export const validateFamPermissionForm = () => {
    return object({
        user: mixed<IdimProxyIdirInfoSchema>()
            .required("A valid user is required")
            .test("is-user-found", "A valid user ID is required", (value) => {
                return value?.found === true;
            }),
        application: mixed<FamApplicationDto>().required(
            "Please select an application"
        ),
    });
};

export const generatePayload = (
    formData: FamPermissionFormType
): FamAppAdminCreateRequest => ({
    user_name: formData.user?.userId ?? "",
    user_guid: formData.user?.guid ?? "",
    user_type_code: UserType.I,
    application_id: formData.application?.id ?? -1,
});
