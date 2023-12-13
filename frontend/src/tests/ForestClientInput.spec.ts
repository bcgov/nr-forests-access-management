import { it, describe, beforeEach, expect, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { AxiosResponse } from 'axios';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import ForestClientInput from '@/components/grantaccess/form/ForestClientInput.vue';

const TEST_SUCCESS_FOREST_CLIENT_NUMBER = '00000001';
const TEST_FOREST_CLIENT_NAME = 'MANAGEMENT ABEYANCE';

const testSuccessSearchResponse: AxiosResponse = {
    data: [
        {
            client_name: TEST_FOREST_CLIENT_NAME,
            forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER,
            status: {
                status_code: 'A',
                description: 'Active',
            },
        },
    ],
    status: 200,
    statusText: 'Ok',
    headers: {},
    config: {},
};

describe('ForestClientInput', () => {
    let wrapper: VueWrapper;

    beforeEach(async () => {
        vi.spyOn(
            AppActlApiService.forestClientsApi,
            'search'
        ).mockImplementation(() => {
            return Promise.resolve(testSuccessSearchResponse);
        });

        wrapper = mount(ForestClientInput, {
            props: {
                userId: 'testUser',
            },
        });
    });

    it('should render forest client number input field', () => {
        expect(wrapper.html().includes('User’s Client ID (8 digits)')).toBe(
            true
        );
        expect(wrapper.find('#forestClientInput').exists()).toBe(true);
        // no forest client card is displayed initially
        expect(wrapper.html().includes('Verified Client ID information')).toBe(
            false
        );
    });

    it('add success forest client number', async () => {
        const input = wrapper.find('#forestClientInput');
        await input.setValue('00000001');
        expect(input.element.value).toBe('00000001');

        const verifyButton = wrapper.find("[aria-label='Add Client Numbers']");
        await verifyButton.trigger('click');
        await flushPromises();

        const setVerifiedForestClients = wrapper.emitted(
            'setVerifiedForestClients'
        );
        // setVerifiedForestClients has been called when verification is successful
        expect(wrapper.emitted()).toHaveProperty('setVerifiedForestClients');
        // has been called once
        expect(setVerifiedForestClients).toHaveLength(1);
        // test the given parameters when setVerifiedForestClients has been called
        // i.e. setVerifiedForestClients = [ [ '00000001' ] ]
        // the outter array indicates how many times it has been called
        // the inner array indicates how many parameters it has
        expect(setVerifiedForestClients[0][0]).toEqual(
            TEST_SUCCESS_FOREST_CLIENT_NUMBER
        );
        // the forest client information card shows and verify the information
        expect(wrapper.html().includes('Verified Client ID information')).toBe(
            true
        );
        expect(
            wrapper
                .find('.client-id-wrapper')
                .text()
                .includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)
        ).toBe(true);
        expect(
            wrapper
                .find('.org-name-wrapper')
                .text()
                .includes(TEST_FOREST_CLIENT_NAME)
        ).toBe(true);
        expect(
            wrapper.find('.org-status-wrapper').text().includes('Active')
        ).toBe(true);
        // the forest client input should now be empty
        expect(input.element.value).toBe('');
    });
});
