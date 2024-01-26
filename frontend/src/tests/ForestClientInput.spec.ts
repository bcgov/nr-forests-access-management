import { it, describe, beforeEach, expect, vi, afterEach } from 'vitest';
import { DOMWrapper, flushPromises, mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import ForestClientInput from '@/components/grantaccess/form/ForestClientInput.vue';
import {
    STATUS_CODE_ACTIVE,
    STATUS_CODE_INACTIVE,
    STATUS_DESCRIPTION_ACTIVE,
    STATUS_DESCRIPTION_INACTIVE,
    TEST_FOREST_CLIENT_NAME,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER,
    TEST_INVALID_FOREST_CLIENT_NUMBER,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER_2,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER_3
} from './common/ForestClientData';
import { isLoading, setLoadingState } from '@/store/LoadingState';
import type { AxiosRequestHeaders, AxiosResponse } from 'axios';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr()

const forestClientsApiSearchMock = (forestClientNumber: string): AxiosResponse => {
    return {
        data: forestClientNumber === TEST_INVALID_FOREST_CLIENT_NUMBER ? [] : [
            {
                client_name: `${TEST_FOREST_CLIENT_NAME}_${forestClientNumber}`,
                forest_client_number: forestClientNumber,
                status: forestClientNumber === TEST_INACTIVE_FOREST_CLIENT_NUMBER ? {
                    status_code: STATUS_CODE_INACTIVE,
                    description: STATUS_DESCRIPTION_INACTIVE,
                }
                    : {
                        status_code: STATUS_CODE_ACTIVE,
                        description: STATUS_DESCRIPTION_ACTIVE,
                    },
            },
        ],
        status: 200,
        statusText: 'Ok',
        headers: {},
        config: {
            headers: {} as AxiosRequestHeaders
        },
    };
}

describe('ForestClientInput', () => {
    let wrapper: VueWrapper;

    let input: DOMWrapper<HTMLElement>;
    let inputField: HTMLInputElement;

    beforeEach(async () => {
        vi.spyOn(
            AppActlApiService.forestClientsApi,
            'search'
        ).mockImplementation(async (item) => {
            return Promise.resolve(forestClientsApiSearchMock(item));
        });
        wrapper = mount(ForestClientInput, {
            props: {
                userId: 'testUser',
            },
        });
        input = wrapper.find('#forestClientInput');
        inputField = input.element as HTMLInputElement;
    });

    afterEach(() => {
        vi.clearAllMocks();
        wrapper.unmount();
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
        // Verify if the Add button is rendered and it is disabled
        const verifyButton = wrapper.find("[aria-label='Add Client Numbers']");
        expect(verifyButton.html().includes('Add Client Numbers')).toBe(true);
        expect((verifyButton.element as HTMLButtonElement).disabled).toBe(true);
    });

    it('should add active forest client number', async () => {

        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
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
        expect(setVerifiedForestClients![0][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // the forest client information card shows and verify the information
        expect(wrapper.html().includes('Verified Client ID information')).toBe(
            true
        );
        expect(
            wrapper
                .find('#forest-client-id')
                .text()
                .includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)
        ).toBe(true);
        expect(
            wrapper
                .find('#forest-client-name')
                .text()
                .includes(TEST_FOREST_CLIENT_NAME)
        ).toBe(true);
        expect(
            wrapper.find('#forest-client-status').text().includes('Active')
        ).toBe(true);
        // the forest client input should now be empty
        expect(inputField.value).toBe('');
    });

    it('should raise error for forest client number not found', async () => {
        await input.setValue(TEST_INVALID_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INVALID_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();
        expect(wrapper.find('#forestClientInputValidationError').element.textContent).contain(`Client ID ${TEST_INVALID_FOREST_CLIENT_NUMBER} is invalid and cannot be added.`);
    });

    it('should raise error for inactive forest client number', async () => {
        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).contain(`Client ID ${TEST_INACTIVE_FOREST_CLIENT_NUMBER} is inactive and cannot be added.`);
    });

    it('should raise error for duplicate user input', async () => {
        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);

        const verifyButton = wrapper.find("[aria-label='Add Client Numbers']");
        await verifyButton.trigger('click');
        await flushPromises();

        // Check if the forest client number has been added to the card
        expect(wrapper.html().includes('Verified Client ID information')).toBe(true);

        // Try to add the same client number again
        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);

        await verifyButton.trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).contain(`Client ID ${TEST_SUCCESS_FOREST_CLIENT_NUMBER} has already been added.`);
        // The input field should still display the duplicate input
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // Expect the card to have just one entry
        expect(wrapper.findAll('#forest-client-name')).toHaveLength(1);
    });

    it('should add multiple active forest client numbers', async () => {
        const multipleSuccessInputs = `${TEST_SUCCESS_FOREST_CLIENT_NUMBER},${TEST_SUCCESS_FOREST_CLIENT_NUMBER_2},${TEST_SUCCESS_FOREST_CLIENT_NUMBER_3}`
        await input.setValue(multipleSuccessInputs);
        expect(inputField.value).toBe(multipleSuccessInputs);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const setVerifiedForestClients = wrapper.emitted('setVerifiedForestClients');
        // setVerifiedForestClients has been called when verification is successful
        expect(wrapper.emitted()).toHaveProperty('setVerifiedForestClients');
        expect(setVerifiedForestClients).toHaveLength(3);
        // The first entry in the forest client card should be equal to the first active input
        expect(setVerifiedForestClients![0][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The second entry in the forest client card should be equal to the second active input
        expect(setVerifiedForestClients![1][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
        // The third entry in the forest client card should be equal to the third active input
        expect(setVerifiedForestClients![2][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_3);
        // the forest client information card shows and verify the information
        expect(wrapper.html().includes('Verified Client ID information')).toBe(
            true
        );
        const clientIdCardList = wrapper.findAll('#forest-client-id');
        const clientNameCardList = wrapper.findAll('#forest-client-name');
        const clientStatusCardList = wrapper.findAll('#forest-client-status');

        expect(clientIdCardList).toHaveLength(3);

        expect(clientIdCardList[0].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)).toBe(true);
        expect(clientNameCardList[0].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)).toBe(true);  // Name is composed by TEST_{ID}, so checking only if ID is present
        expect(clientStatusCardList[0].text().includes('Active')).toBe(true);

        expect(clientIdCardList[1].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2)).toBe(true);
        expect(clientNameCardList[1].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2)).toBe(true);
        expect(clientStatusCardList[1].text().includes('Active')).toBe(true);

        expect(clientIdCardList[2].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER_3)).toBe(true);
        expect(clientNameCardList[2].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER_3)).toBe(true);
        expect(clientStatusCardList[2].text().includes('Active')).toBe(true);
        // the forest client input should now be empty
        expect(inputField.value).toBe('');
    });

    it('should add active forest client numbers and raise errors for inactive and invalid numbers in multiple input', async () => {
        // Mutiple inputs: two valid ones, one invalid and one inactive
        const mixedInputs = `${TEST_SUCCESS_FOREST_CLIENT_NUMBER},${TEST_INACTIVE_FOREST_CLIENT_NUMBER},${TEST_INVALID_FOREST_CLIENT_NUMBER},${TEST_SUCCESS_FOREST_CLIENT_NUMBER_2}`
        await input.setValue(mixedInputs);
        expect(inputField.value).toBe(mixedInputs);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const setVerifiedForestClients = wrapper.emitted(
            'setVerifiedForestClients'
        );
        expect(wrapper.emitted()).toHaveProperty('setVerifiedForestClients');
        // has been called twice because we have two active ones
        expect(setVerifiedForestClients).toHaveLength(2);

        const validationError = wrapper.findAll('#forestClientInputValidationError');
        // we need to have two error messages as well (inactive and invalid)
        expect(validationError).toHaveLength(2);
        // The first entry in the forest client card should be equal to the first active input
        expect(setVerifiedForestClients![0][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The second entry in the forest client card should be equal to the second active input
        expect(setVerifiedForestClients![1][0]).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
        // the forest client information card shows and verify the information
        expect(wrapper.html().includes('Verified Client ID information')).toBe(
            true
        );
        expect(
            wrapper
                .find('#forest-client-id')
                .text()
                .includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)
        ).toBe(true);
        expect(
            wrapper
                .find('#forest-client-name')
                .text()
                .includes(TEST_FOREST_CLIENT_NAME)
        ).toBe(true);
        expect(
            wrapper.find('#forest-client-status').text().includes('Active')
        ).toBe(true);
        // the forest client input should still display the error input numbers
        expect(inputField.value).toContain(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toContain(TEST_INVALID_FOREST_CLIENT_NUMBER);

        const clientIdCardList = wrapper.findAll('#forest-client-id');

        expect(clientIdCardList).toHaveLength(2);

        expect(clientIdCardList[0].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)).toBe(true);
        expect(clientIdCardList[1].text().includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2)).toBe(true);
    });

    it('should test the adding button in on loading while we call the api', async () => {
        vi.spyOn(
            AppActlApiService.forestClientsApi,
            'search'
        ).mockImplementation(async (item) => {
            // here we suppose while we call backend api, the loading state will be true
            setLoadingState(true);
            return forestClientsApiSearchMock(item);
        });
        const input = wrapper.find('#forestClientInput');
        const inputField = input.element as HTMLInputElement;
        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        await wrapper
            .find("[aria-label='Add Client Numbers']")
            .trigger('click');
        expect(isLoading()).toBe(true);
        expect(
            wrapper.find("[aria-label='Add Client Numbers']").element
                .textContent
        ).contains('Loading');

        // cleanup state variable
        setLoadingState(false);
    });

    it('should test the delete forest client number case', async () => {
        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.findAll('#forest-client-id')).toHaveLength(1);

        const deleteButton = wrapper.find('#btn-trash-can');
        deleteButton.trigger('click');
        await flushPromises();

        expect(wrapper.findAll('#forest-client-id')).toHaveLength(0);

        // removeVerifiedForestClients has been called when delete is clicked
        expect(wrapper.emitted()).toHaveProperty('removeVerifiedForestClients');
    });

    it('should cleanup error when input change', async () => {
        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        // Check if the error message has been raised
        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();

        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The error message should be cleared
        expect(wrapper.find('#forestClientInputValidationError').exists()).toBeFalsy();
    });

    it('should cleanup forest client card when property change', async () => {
        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const clientIdCardList = wrapper.findAll('#forest-client-id');
        expect(clientIdCardList).toHaveLength(1);

        // Changing the userId prop should cleanUp Forest Client Card
        await wrapper.setProps({ userId: 'Test' });

        expect(wrapper.emitted()).toHaveProperty('resetVerifiedForestClients');

        // The forest client card should be cleared
        expect(wrapper.findAll('#forest-client-id')).toHaveLength(0);

        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.findAll('#forest-client-id')).toHaveLength(1);

        // Changing the roleId prop should cleanUp Forest Client Card
        await wrapper.setProps({ roleId: 1 });

        expect(wrapper.emitted()).toHaveProperty('resetVerifiedForestClients');

        expect(wrapper.findAll('#forest-client-id')).toHaveLength(0);

    });

    it('should cleanup forest client number when property change', async () => {
        await input.setValue(TEST_INVALID_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INVALID_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();

        expect(inputField.value).toBe(TEST_INVALID_FOREST_CLIENT_NUMBER);

        // Changing the userId prop should cleanUp Input
        await wrapper.setProps({ userId: 'Test' });

        expect(inputField.value).toBe('');

        expect(wrapper.emitted()).toHaveProperty('resetVerifiedForestClients');

        expect(wrapper.find('#forestClientInputValidationError').exists()).toBeFalsy();

        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();

        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        // Changing the roleId prop should cleanUp Input
        await wrapper.setProps({ roleId: 1 });

        expect(inputField.value).toBe('');

        expect(wrapper.emitted()).toHaveProperty('resetVerifiedForestClients');

        expect(wrapper.find('#forestClientInputValidationError').exists()).toBeFalsy();

    });
});
