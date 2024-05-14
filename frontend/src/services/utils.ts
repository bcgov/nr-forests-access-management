import { number, object, string } from 'yup';

type AsyncWrapType = {
    data: any;
    error: any;
};

/**
 * This is for use in case if you need to warp normal async return
 * (promise's resolve or reject) so you can await for it and use
 * normal "if (data)/else { handle error}" than typical try-catch.
 * @param promise Promise()
 * @returns '{data, error}' in tuple containing 'data' (underfined when 'error' present).
 */
export const asyncWrap = async (
    promise: Promise<any>
): Promise<AsyncWrapType> => {
    try {
        const data = await promise;
        return { data, error: undefined };
    } catch (error) {
        return { data: undefined, error };
    }
};

export const formValidationSchema = (isAbstractRoleSelected: boolean) => {
    return object({
        userId: string()
            .required('User ID is required')
            .min(2, 'User ID must be at least 2 characters')
            .nullable(),
        roleId: number().required('Please select a value'),
        forestClientNumbers: string()
            .when('roleId', {
                is: (_role_id: number) => isAbstractRoleSelected,
                then: () =>
                    string()
                        .nullable()
                        .transform((curr, orig) => (orig === '' ? null : curr)) // Accept either null or value
                        .matches(
                            //string of eight digits separeted by commas and optional whitespace
                            /^\s*\d{8}(\s*,\s*\d{8})*\s*$/,
                            'Please enter a Forest Client ID with 8 digits long'
                        ),
            })
            .nullable(),
    });
};
