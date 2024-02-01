import { it, describe, beforeEach, afterEach, expect, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { UserType } from 'fam-app-acsctl-api';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import { isLoading, setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosRequestHeaders, AxiosResponse } from 'axios';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr();

const userInputMock = (isUserFound: boolean): AxiosResponse => {
    if (isUserFound) {
        return {
            data: {
                firstName: 'Name',
                found: true,
                lastName: 'LastName',
                userId: 'UserId',
            },
            status: 200,
            statusText: 'Ok',
            headers: {},
            config: {
                headers: {} as AxiosRequestHeaders,
            },
        };
    } else {
        return {
            data: {
                found: false,
                userId: 'userId',
            },
            status: 200,
            statusText: 'Ok',
            headers: {},
            config: {
                headers: {} as AxiosRequestHeaders,
            },
        };
    }
};

describe('UserNameInput', () => {
    let wrapper: VueWrapper;

    let usernameInputText: DOMWrapper<HTMLElement>;
    let usernameInputTextEl: HTMLInputElement;
    let verifyButton: DOMWrapper<HTMLElement>;
    let verifyButtonEl: HTMLButtonElement;
    let cardEl: HTMLSpanElement

    const props = {
        domain: UserType.I,
        userId: '',
        fieldId: 'userId',
    };

    const newProps = {
        domain: UserType.B,
        userId: 'newUserId',
        fieldId: 'newFieldId',
    };

    const newValue = 'testIdir';

    beforeEach(async () => {
        wrapper = mount(UserNameInput, {
            props,
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
        expect(usernameInputTextEl.value).toBe('');
        await usernameInputText.setValue(newValue);
        expect(usernameInputTextEl.value).toBe(newValue);
    });

    it('Should receive the correct prop', async () => {
        //default props
        expect(wrapper.props()).toEqual(props);

        await wrapper.setProps(newProps);
        expect(wrapper.props()).toEqual(newProps);
        expect(wrapper.props()).not.toEqual(props);
    });

    it('Should call and emit correct value', async () => {
        await usernameInputText.setValue(newValue);
        const emitChange = wrapper.emitted('change');
        expect(emitChange).toBeTruthy();
        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(emitChange![0][0]).toEqual(newValue);
    });

    it('Should enable verify btn when username is inputted', async () => {
        expect(usernameInputTextEl.value).toBe('')
        // button starts as disabled
        expect(verifyButtonEl.disabled).toBe(true);
        expect(verifyButton.classes('p-disabled')).toBe(true);

        await wrapper.setProps({ userId: newProps.userId });

        expect(verifyButtonEl.disabled).toBe(false);
        expect(verifyButton.classes('p-disabled')).toBe(false);
    });

    it('Should show loading on the verify btn while we call the api', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            setLoadingState(true);
            return userInputMock(true);
        });
        expect(verifyButtonEl.textContent).not.toContain('Loading');

        await wrapper.setProps({ userId: newProps.userId });
        await verifyButton.trigger('click');
        expect(isLoading()).toBe(true);
        expect(verifyButtonEl.textContent).toContain('Loading');

        // cleanup state variable
        setLoadingState(false);
        expect(isLoading()).toBe(false);
    });

    it('Should show not found on card when user is not found', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            return userInputMock(false);
        });

        //enable verifyButton
        await wrapper.setProps({ userId: newProps.userId });
        await verifyButton.trigger('click');
        await flushPromises();

        wrapper.findComponent({name: 'UserIdentityCard'}).vm;

        cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;
        expect(cardEl).toBeTruthy();
        expect(cardEl.textContent).toContain('User does not exist');
    });

    it('Should remove card and emit different value when domain changes', async () => {
        // show user identity card to prepare for the test
        await wrapper.setProps({ userId: newProps.userId });
        await verifyButton.trigger('click');
        await flushPromises();
        const cardUsernameEl = wrapper.find('#userId').element as HTMLSpanElement;
        expect(cardUsernameEl).toBeTruthy();

        // change the domain to be B
        await wrapper.setProps({domain: UserType.B});
        // for BCeID should emit true
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult![0][0]).toEqual(true);
        //UserIdentityCard not on page anymore
        expect(wrapper.findAll('#UserIdentityCard')).toHaveLength(0);

        // change the domain to be I
        await wrapper.setProps({domain: UserType.I});
        // for IDIR should emit false
        expect(emitSetVerifyResult![1][0]).toEqual(false);
    });

    it('Should show the card with correct info when user is found', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            return userInputMock(true);
        });

        //enable verifyButton
        await wrapper.setProps({ userId: newProps.userId });
        await verifyButton.trigger('click');
        await flushPromises();

        wrapper.findComponent({name: 'UserIdentityCard'}).vm;

        cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;
        expect(cardEl).toBeTruthy();
        expect(cardEl.textContent).toContain('Name');
        expect(cardEl.textContent).toContain('LastName');
        expect(cardEl.textContent).toContain('UserId');
    })

});
