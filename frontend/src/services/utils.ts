
/**
 * This is for use in case if you need to warp normal async return
 * (promise's resolve or reject) so you can await for it and use
 * normal "if (data)/else { handle error}" than typical try-catch.
 * @param promise Promise()
 * @returns '{data, error}' in tuple containing 'data' (underfined when 'error' present).
 */
const asyncWrap = async (promise: Promise<any>) => {
    try {
        const data = await promise;
        return {data, error: undefined};
    } catch (error) {
        return {data: undefined, error}
    }
}