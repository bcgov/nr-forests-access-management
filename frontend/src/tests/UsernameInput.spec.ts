import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { UserType } from 'fam-app-acsctl-api';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';

//fix Could not parse CSS stylesheet with the primevue styling
//https://github.com/primefaces/primevue/issues/4512
const originalConsoleError = console.error;
const jsDomCssError = "Error: Could not parse CSS stylesheet";
console.error = (...params) => {
  if (!params.find((p) => p.toString().includes(jsDomCssError))) {
    originalConsoleError(...params);
  }
};


describe('UserNameInput', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;
    let emitSetVerifyResult: unknown[][] | undefined;

    let usernameInputText: DOMWrapper<HTMLElement>;
    let usernameInputTextEl: HTMLInputElement;
    let verifyButton: DOMWrapper<HTMLElement>;

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
        wrapper = mount(UserNameInput, {
            props,
            global: {
                plugins: [PrimeVue, ],
            },
        });
        usernameInputText = wrapper.find('#userIdInput');
        usernameInputTextEl = usernameInputText.element as HTMLInputElement;
        verifyButton = wrapper.find("[aria-label='Verify user IDIR']");
    });

    it('should change usernameInput value', async () => {
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
        await usernameInputText.setValue(inputString);

        emitChange = wrapper.emitted('change');
        expect(wrapper.emitted('change')).toBeTruthy();
        expect(emitChange![0][0]).toEqual(inputString);


        emitSetVerifyResult = wrapper.emitted('setVerifyResult')
        await wrapper.setProps(newProps);
        await verifyButton.trigger('click');

        console.log(emitSetVerifyResult)
        expect(wrapper.emitted('setVerifyResult')).toBeTruthy();
        expect(emitSetVerifyResult![1][0]).toEqual(true);

        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        // expect(emitChange![0][0]).toEqual(UserType.B);

        // await idirRadioBtn.trigger('click');

        // expect(emitChange![1][0]).toEqual(UserType.I);
    })

})