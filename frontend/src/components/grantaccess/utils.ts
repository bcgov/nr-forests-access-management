import { number, object, string } from "yup";

/**
 * Validation schema for app admin and delegated admin
 */
export const validateAppAndDeAdminForm = (isAbstractRoleSelected: boolean) => {
    return object({
        userId: string()
            .required("User ID is required")
            .min(2, "User ID must be at least 2 characters")
            .nullable(),
        roleId: number().required("Please select a value"),
        forestClientNumbers: string()
            .when("roleId", {
                is: (_role_id: number) => isAbstractRoleSelected,
                then: () =>
                    string()
                        .nullable()
                        .transform((curr, orig) => (orig === "" ? null : curr)) // Accept either null or value
                        .matches(
                            //string of eight digits separeted by commas and optional whitespace
                            /^\s*\d{8}(\s*,\s*\d{8})*\s*$/,
                            "Please enter a Forest Client Number with 8 digits long"
                        ),
            })
            .nullable(),
    });
};
