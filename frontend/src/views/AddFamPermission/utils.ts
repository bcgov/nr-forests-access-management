import type { SelectUser } from "@/types/SelectUserType";
import type {
    FamAppAdminCreateRequest,
    FamApplicationGrantDto,
} from "fam-admin-mgmt-api/model";
import { UserType } from "fam-app-acsctl-api";
import { mixed, object } from "yup";

export const AddAppAdminSuccessQueryKey = "app-admin-success";
export const AddAppAdminErrorQueryKey = "app-admin-error";

export const NewAppAdminQueryParamKey = "newAppAdminIds";

export type AppAdminFormType = {
    user: SelectUser | null;
    application: FamApplicationGrantDto | null;
};

const defaultFormData: AppAdminFormType = {
    user: null,
    application: null,
};

export const getDefaultFormData = (): AppAdminFormType =>
    structuredClone(defaultFormData);

/**
 * Validation schema for application admin
 */
export const validateAppAdminForm = () => {
    console.log("Validating app admin form");
    return object({
        user: mixed<SelectUser>()
            .required("A valid user is required"),
            // .test("is-user-found", "A valid user ID is required", (value) => {
            //     return value?.found === true;
            // }),
        application: mixed<FamApplicationGrantDto>().required(
            "Please select an application"
        ),
    });
};

export const generatePayload = (
    formData: AppAdminFormType
): FamAppAdminCreateRequest => ({
    user_name: formData.user?.userId ?? "",
    user_guid: formData.user?.guid ?? "",
    user_type_code: UserType.I,
    application_id: formData.application?.id ?? -1,
});
