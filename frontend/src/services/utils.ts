import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { isSelectedAppProd } from "@/store/ApplicationState";

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

export const isNewAccess = (newAccessIds: string[], accessId: number) => {
    return newAccessIds.includes(accessId.toString());
};

export const isProdAppSelectedOnProdEnv = () => {
    const isProdEnvironment = new EnvironmentSettings().isProdEnvironment();
    return isProdEnvironment && isSelectedAppProd.value;
};
