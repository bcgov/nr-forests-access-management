import { getNavigationPath, removeNavigationPath, setNavigationPath } from '@/store/NavigationState';
import { it, describe, expect } from 'vitest';

describe('NavigationState', () => {
    it('should set NavigationPath', async () => {

        setNavigationPath('/test');
        expect(getNavigationPath()).toBe('/test');
    });

    it('should clear NavigationPath', async () => {
        setNavigationPath('/test');
        removeNavigationPath();
        expect(getNavigationPath()).toBeNull();
    });
});