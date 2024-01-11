import { it, describe, expect, vi } from 'vitest';
import { getToastErrorMsg } from '@/store/ToastState';
import type { FamCustomError } from '@/errors/FamCustomError';

const generalError: FamCustomError = {
    message: 'Test error message',
    cause: undefined,
    name: 'Test'
}

describe('ToastState', () => {
    it('should throw generic error message', async () => {
        const testErrorMessage = getToastErrorMsg(generalError);
        expect(testErrorMessage).toBe('An application error has occurred. Please try again. If the error persists contact support.')
    });
});