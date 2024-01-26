import { it, describe, beforeEach, afterEach, expect, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { UserType } from 'fam-app-acsctl-api';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import { isLoading, setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosResponse } from 'axios';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr()


const userInputMock = (): AxiosResponse => {
    return {
        data: {
            firstName: "Name",
            found: true,
            lastName: "LastName",
            userId: 'userId'
        },
        status: 200,
        statusText: 'Ok',
        headers: {},
        config: {},
    }

}

describe('UserNameInput', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;
    let emitSetVerifyResult: unknown[][] | undefined;

    let usernameInputText: DOMWrapper<HTMLElement>;
    let usernameInputTextEl: HTMLInputElement;
    let verifyButton: DOMWrapper<HTMLElement>;
    let verifyButtonEl: HTMLButtonElement;

    let cardUsernameEl: HTMLSpanElement;
    let verifiedUserIdentity

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

    const newValue = 'testIdir';

    beforeEach(async () => {
        wrapper = mount(UserNameInput, {
            props,
            global: {
                plugins: [PrimeVue],
            },
        });

        usernameInputText = wrapper.find('#userIdInput');
        usernameInputTextEl = usernameInputText.element as HTMLInputElement;
        verifyButton = wrapper.find("[data-target-btn='verifyIdir']");
        verifyButtonEl = verifyButton.element as HTMLButtonElement;
    });

    afterEach(() => {
        vi.clearAllMocks();
        wrapper.unmount();
    });

    it('Should change usernameInput value', async () => {
        await usernameInputText.setValue(newValue);
        expect(usernameInputTextEl.value).toBe(newValue);
    });

    it('Should receive the correct prop', async () => {
        //default props
        expect(wrapper.props()).toEqual(props);

         await wrapper.setProps(newProps);
         expect(wrapper.props()).toEqual(newProps);
         expect(wrapper.props()).not.toEqual(props)
    });

    it('Should call and emit correct value' , async () => {
        await usernameInputText.setValue(newValue);
        emitChange = wrapper.emitted('change');
        expect(wrapper.emitted('change')).toBeTruthy();
        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(emitChange![0][0]).toEqual(newValue);

        emitSetVerifyResult = wrapper.emitted('setVerifyResult')
        await wrapper.setProps(newProps);
        await verifyButton.trigger('click');

        expect(wrapper.emitted('setVerifyResult')).toBeTruthy();
        expect(emitSetVerifyResult![1][0]).toEqual(true);
    });

    it('Should enable verify btn when username is inputted', async () => {
        // button starts as disabled
        expect((verifyButtonEl).disabled).toBe(true)
        expect(verifyButton.classes('p-disabled')).toBe(true);

        await wrapper.setProps({userId: newProps.userId })

        expect((verifyButtonEl).disabled).toBe(false)
        expect(verifyButton.classes('p-disabled')).toBe(false);
    });

    it('Should show loading on the verify btn while we call the api' , async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch',
        ).mockImplementation(async () => {
            setLoadingState(true);
            return userInputMock();
        });

        await usernameInputText.setValue(newValue);
        expect(usernameInputTextEl.value).toBe(newValue);

        await wrapper.setProps({ userId: newProps.userId });
        await verifyButton.trigger('click');
        expect(isLoading()).toBe(true);
        expect(verifyButtonEl.textContent).toContain('Loading');

        // cleanup state variable
        setLoadingState(false);
        expect(isLoading()).toBe(false)
    });

    it('Should remove card and emit different value when domain changes', async () => {
        emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        // default props
        expect(wrapper.props()).toEqual(props);

        await usernameInputText.setValue(newValue);
        expect(usernameInputTextEl.value).toEqual(newValue);

        await wrapper.setProps(userInputMock().data);
        await verifyButton.trigger('click');
        await flushPromises();

        verifiedUserIdentity = wrapper.findComponent({ name: 'UserIdentityCard'}).vm;
        verifiedUserIdentity = userInputMock().data
        cardUsernameEl = wrapper.find('#userId').element as HTMLSpanElement;
        expect(cardUsernameEl).toBeTruthy();
        expect(cardUsernameEl.textContent).toContain('userId');

        await wrapper.setProps({
            domain: UserType.B,
        });

        expect(wrapper.emitted()).toHaveProperty('setVerifyResult');

        // for BCeID should emit true
        expect(wrapper.emitted().setVerifyResult[1][0]).toEqual(true);

        //UserIdentityCard not em page anymore
        expect(wrapper.findAll('#UserIdentityCard')).toHaveLength(0);
    });
})