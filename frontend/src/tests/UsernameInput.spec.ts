import { it, describe, beforeEach, afterEach, expect, vi } from 'vitest';
import { mount, flushPromises  } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { UserType } from 'fam-app-acsctl-api';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import { isLoading, setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosResponse } from 'axios';

//fix "Could not parse CSS stylesheet" with the primevue styling
//https://github.com/primefaces/primevue/issues/4512
//https://stackoverflow.com/questions/69906136/console-error-error-could-not-parse-css-stylesheet/69958999#69958999
const originalConsoleError = console.error;
const jsDomCssError = "Error: Could not parse CSS stylesheet";
console.error = (...params) => {
  if (!params.find((p) => p.toString().includes(jsDomCssError))) {
    originalConsoleError(...params);
  }
};

const userInputMock = (): AxiosResponse => {
    return {
        data: {
            firstName: "Name",
            found: true,
            lastName: "LastName",
            userId: "Userid"
        },
        status: 200,
        statusText: 'Ok',
        headers: {},
        config: {},
    };
}

describe('UserNameInput', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;
    let emitSetVerifyResult: unknown[][] | undefined;

    let usernameInputText: DOMWrapper<HTMLElement>;
    let usernameInputTextEl: HTMLInputElement;
    let verifyButton: DOMWrapper<HTMLElement>;
    let verifyButtonEl: HTMLButtonElement;

    const props = {
        domain: UserType.I,
        userId: '',
        fieldId: 'userId',
    }

    const newProps = {
        domain: UserType.B,
        userId: 'newUserId',
        fieldId: 'newFieldId',
    };

    const inputString = 'testIdir';

    beforeEach(async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch',
        ).mockImplementation(async () => {
            return Promise.resolve(userInputMock());
        });
        wrapper = mount(UserNameInput, {
            props,
            global: {
                plugins: [PrimeVue],
            },
        });
        // usernameInputText = wrapper.find('#userIdInput');
        // usernameInputTextEl = usernameInputText.element as HTMLInputElement;
        // verifyButton = wrapper.find("[data-target-btn='verifyIdir']");
        // verifyButtonEl = verifyButton.element as HTMLButtonElement;
    });

    afterEach(() => {
        vi.clearAllMocks();
        wrapper.unmount();
    });

    it('should change usernameInput value', async () => {
        usernameInputText = wrapper.find('#userIdInput');
        usernameInputTextEl = usernameInputText.element as HTMLInputElement;
        await usernameInputText.setValue(inputString);
        expect(usernameInputTextEl.value).toBe(inputString);
    });

    it('Should receive the correct prop', async () => {
        //default props
        expect(wrapper.props()).toEqual(props);

         await wrapper.setProps(newProps);
         expect(wrapper.props()).toEqual(newProps);
         expect(wrapper.props()).not.toEqual(props)
    });

    it('Should call and emit value' , async () => {
        usernameInputText = wrapper.find('#userIdInput');
        usernameInputTextEl = usernameInputText.element as HTMLInputElement;
        verifyButton = wrapper.find("[data-target-btn='verifyIdir']");
        verifyButtonEl = verifyButton.element as HTMLButtonElement;
        await usernameInputText.setValue(inputString);

        emitChange = wrapper.emitted('change');
        expect(wrapper.emitted('change')).toBeTruthy();
        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(emitChange![0][0]).toEqual(inputString);


        emitSetVerifyResult = wrapper.emitted('setVerifyResult')
        await wrapper.setProps(newProps);
        await verifyButton.trigger('click');


        expect(wrapper.emitted('setVerifyResult')).toBeTruthy();
        expect(emitSetVerifyResult![1][0]).toEqual(true);
    });

    it('should enable virify btn when username is inputted', async () => {
        usernameInputText = wrapper.find('#userIdInput');
        await usernameInputText.setValue(inputString);
        emitChange = wrapper.emitted('change');
        expect(wrapper.emitted('change')).toBeTruthy();
        verifyButton = wrapper.find("[data-target-btn='verifyIdir']")
        console.log((verifyButton.element as HTMLButtonElement).disabled)
        expect((verifyButton.element as HTMLButtonElement).disabled).toBe(false);
    });

    // it('should display information on card correctly based on api response ' , async () => {
    //     vi.spyOn(
    //         AppActlApiService.idirBceidProxyApi,
    //         'idirSearch',
    //     ).mockImplementation(async () => {
    //         setLoadingState(true);
    //         return Promise.resolve(userInputMock());
    //     });
    //     await usernameInputText.setValue(inputString);
    //     expect(usernameInputTextEl.value).toBe(inputString);

    //     await verifyButton.trigger('click');
    //     // expect(isLoading()).toBe(true);
    // })

})