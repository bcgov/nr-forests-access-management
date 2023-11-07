import ProtectedLayout from '@/layouts/ProtectedLayout.vue';
import { flushPromises, shallowMount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import { it, describe, expect, beforeEach } from 'vitest';

import sideNavData from '@/static/sideNav.json';
describe('disableSideNavOption', () => {
    let wrapper: VueWrapper;

    beforeEach(async () => {
        wrapper = shallowMount(ProtectedLayout);
        await flushPromises();
    });
    it('should change value for navigation option Add user permission', async () => {
        (wrapper.vm as any).disableSideNavOption('Add user permission', false);
        let value = sideNavData.map(item => item.items.find(child => child.name === 'Add user permission')?.disabled)[0];
        expect(value).toBe(false)
    });
});