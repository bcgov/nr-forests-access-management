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
import type { AxiosResponse } from 'axios';

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
        config: {},
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
            setLoadingState(true);
            return Promise.resolve(async () => {
                setTimeout(() => { }, 5000);
            }).then(() => {
                return forestClientsApiSearchMock(item)
            }).finally(() => setLoadingState(false));
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
        expect(verifyButton.element.disabled).toBe(true);
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
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[0][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
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
        expect(inputField.value).toBe('');
    });

    it('should raise error for forest client number not found', async () => {
        await input.setValue(TEST_INVALID_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INVALID_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();
    });

    it('should raise error for inactive forest client number', async () => {
        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();
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

        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();
        //The input field should still display the duplicate input
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
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
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[0][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The second entry in the forest client card should be equal to the second active input
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[1][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
        // The third entry in the forest client card should be equal to the third active input
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[2][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_3);
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
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[0][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The second entry in the forest client card should be equal to the second active input
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[1][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
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
        // the forest client input should still display the error input numbers
        expect(inputField.value).toContain(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toContain(TEST_INVALID_FOREST_CLIENT_NUMBER);
    });

    //TODO - The test case below needs to adjust the mockImplementation for the api call to have a non blocking delay
    // so the loadingState and the button label could be tested. I have tried some approaches but none seem to work:
    // - Use of setTimeout doesn't work well in testing (the timout is not applied)
    // - Use of vi.useFakeTimers() does apply delay, but I am not sure if it is a blocking or non blocking task

    // it('should test the adding button in on loading while we call the api', async () => {
    //     const input = wrapper.find('#forestClientInput');
    //     const inputField: HTMLInputElement = input.element as HTMLInputElement;
    //     await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
    //     expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
    //     expect(isLoading()).toBe(false);

    //     await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
    //     await flushPromises();

    //     expect(isLoading()).toBe(true);
    //     expect(wrapper.find("[aria-label='Add Client Numbers']").element.textContent).contains('Loading')
    // });

    it('should test the delete forest client number case', async () => {
        const multipleSuccessInputs = `${TEST_SUCCESS_FOREST_CLIENT_NUMBER},${TEST_SUCCESS_FOREST_CLIENT_NUMBER_2}`;
        await input.setValue(multipleSuccessInputs);
        expect(inputField.value).toBe(multipleSuccessInputs);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const setVerifiedForestClients = wrapper.emitted(
            'setVerifiedForestClients'
        );

        expect(wrapper.emitted()).toHaveProperty('setVerifiedForestClients');
        expect(setVerifiedForestClients).toHaveLength(2);
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[0][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(
            setVerifiedForestClients
                ? setVerifiedForestClients[1][0]
                : undefined
        ).toEqual(TEST_SUCCESS_FOREST_CLIENT_NUMBER_2);
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
        expect(inputField.value).toBe('');

        const deleteButton = wrapper.find('.custom-carbon-icon--trash-can');
        deleteButton.trigger('click');
        await flushPromises();
        expect(
            wrapper
                .find('.client-id-wrapper')
                .text()
                .includes(TEST_SUCCESS_FOREST_CLIENT_NUMBER)
        ).toBe(false);
    });

    it('should cleanup error when property change', async () => {
        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const validationError = wrapper.get('#forestClientInputValidationError');
        const validationErrorElement: HTMLInputElement = validationError.element as HTMLInputElement;
        // Check if the error message has been raised
        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();

        await input.trigger('click');
        await flushPromises();

        await input.setValue(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_SUCCESS_FOREST_CLIENT_NUMBER);
        // The error message should be cleared
        expect(wrapper.find('#forestClientInputValidationError').exists()).toBeFalsy();
    });
    it('should cleanup forest client card when property change', async () => {
        await input.setValue(TEST_INACTIVE_FOREST_CLIENT_NUMBER);
        expect(inputField.value).toBe(TEST_INACTIVE_FOREST_CLIENT_NUMBER);

        await wrapper.find("[aria-label='Add Client Numbers']").trigger('click');
        await flushPromises();

        const validationError = wrapper.get('#forestClientInputValidationError');
        const validationErrorElement: HTMLInputElement = validationError.element as HTMLInputElement;
        // Check if the error message has been raised
        expect(wrapper.find('#forestClientInputValidationError').element.textContent).toBeTruthy();

        // Changing the userId prop should cleanUp Forest Client Card
        await wrapper.setProps({ userId: 'Test' });
        // The forest client card should be cleared
        expect(wrapper.find('#forestClientInputValidationError').exists()).toBeFalsy();
    });
});
