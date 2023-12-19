import { it, describe, beforeEach, expect, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import ForestClientCard from '@/components/grantaccess/ForestClientCard.vue';
import type { FamForestClient } from 'fam-app-acsctl-api';

const testActiveClient: FamForestClient[] = [
    {
        client_name: 'TEST',
        forest_client_number: '00000001',
        status: {
            status_code: 'A',
            description: 'Active',
        },
    }
];

const testInactiveClient: FamForestClient[] = [
    {
        client_name: 'TEST',
        forest_client_number: '00000002',
        status: {
            status_code: 'I',
            description: 'Inactive',
        },
    }
];

describe('ForestClientCard', () => {

    let wrapper: VueWrapper;

    beforeEach(async () => {
        wrapper = mount(ForestClientCard);
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it('should show inactive for forest client card in error case', async () => {
        // Error case
        await wrapper.setProps({ forestClientData: testInactiveClient });
        expect(wrapper.get('.p-tag-value').element.textContent).toBe('Inactive');
    });
    it('should show active forest client card in successful case', async () => {
        // Success case
        await wrapper.setProps({ forestClientData: testActiveClient });
        expect(wrapper.get('.p-tag-value').element.textContent).toBe('Active');

    });
});