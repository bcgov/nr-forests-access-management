import { it, describe, beforeEach, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import AccessRequest from '@/components/AccessRequest.vue';

vi.mock('vue-router', () => ({
    useRoute: vi.fn(() => ({
        value:
        {
            path: '/access-request',
            name: 'accessRequest',
            meta: {
                requiresAuth: true,
                requiresAppSelected: false,
                layout: 'ProtectedLayout',
                hasBreadcrumb: false,
            },
        }
    }))
}));

describe('AccessRequest', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        wrapper = mount(AccessRequest);
    });
    it('should render title and subtitle', async () => {
        expect(wrapper.find('.title').html().includes('Access Request')).toBe(true);
        expect(wrapper.find('.subtitle').html().includes('Request access to FAM')).toBe(true);
    });
});