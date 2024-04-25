import { it, describe, beforeEach, afterEach, expect, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { UserType } from 'fam-app-acsctl-api';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosRequestHeaders, AxiosResponse } from 'axios';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr();

const USERID = 'TestUser';
const FIRSTNAME = 'TestUserFirstName';
const LASTNAME = 'TestUserLastName';

const idimIdirSearchMock = (isUserFound: boolean): AxiosResponse => {
    if (isUserFound) {
        return {
            data: {
                firstName: FIRSTNAME,
                found: true,
                lastName: LASTNAME,
                userId: USERID,
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
                userId: USERID,
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

    const props = {
        domain: UserType.I,
        userId: '',
        fieldId: 'userId',
        helperText: 'Text helper',
    };

    const newProps = {
        domain: UserType.B,
        userId: USERID,
        fieldId: 'testNewFiledId',
        helperText: 'New text helper',
    };

    beforeEach(() => {
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

    it('Should change username input get correct value', async () => {
        expect(usernameInputTextEl.value).toBe('');
        await usernameInputText.setValue(USERID);
        expect(usernameInputTextEl.value).toBe(USERID);
    });

    it('Should receive the correct props', async () => {
        // default props
        expect(wrapper.props()).toEqual(props);

        await wrapper.setProps(newProps);
        expect(wrapper.props()).toEqual(newProps);
        expect(wrapper.props()).not.toEqual(props);
    });

    it('Should call emit change and setVerifyResult when input change', async () => {
        // when username input value change, emit change with new value
        await usernameInputText.setValue(USERID);
        const emitChange = wrapper.emitted('change');
        expect(emitChange).toBeTruthy();
        expect(emitChange![0][0]).toEqual(USERID);
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).toBeTruthy();
        // default prop domain is I, emit setVerifyResult with false
        expect(emitSetVerifyResult![0][0]).toEqual(false);
    });

    it('Should enable verify btn when username is inputted', async () => {
        // input is empty, button starts as disabled
        expect(usernameInputTextEl.value).toBe('');
        expect(verifyButtonEl.disabled).toBe(true);
        expect(verifyButton.classes('p-disabled')).toBe(true);

        // triggers username input change
        await wrapper.setProps({ userId: USERID });
        // verify button is enabled
        expect(verifyButtonEl.disabled).toBe(false);
        expect(verifyButton.classes('p-disabled')).toBe(false);
    });

    it('Should show loading on the verify btn while calling the api', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            setLoadingState(true);
            return idimIdirSearchMock(true);
        });

        // by default, the button text is "Verify"
        expect(verifyButtonEl.textContent).toBe('Verify');

        // triggers username input change to enable the verify button and click
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();
        expect(verifyButtonEl.textContent).toContain('Loading');

        // reset loading state variable
        setLoadingState(false);
    });

    it('Should show the user identity card with correct info when user is found', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            return idimIdirSearchMock(true);
        });

        // by default no identity card display
        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(false);

        // triggers username input change to enable the verify button and click
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();

        // call emit setVerifyResult with true, when prop domain is I, mock api returns user found
        // currently when domain is B, the verify button will be hidden
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).toBeTruthy();
        expect(emitSetVerifyResult![0][0]).toEqual(true);

        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(true);
        const cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;
        // verify identity card title
        expect(cardEl.textContent).toContain('Username');
        expect(cardEl.textContent).toContain('First Name');
        expect(cardEl.textContent).toContain('Last Name');
        // verify identity card user info
        expect(wrapper.find('#userId').element.textContent).toContain(USERID);
        expect(wrapper.find('#firstName').element.textContent).toContain(
            FIRSTNAME
        );
        expect(wrapper.find('#lastName').element.textContent).toContain(
            LASTNAME
        );
    });

    it('Should show not found on card when user is not found', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'idirSearch'
        ).mockImplementation(async () => {
            return idimIdirSearchMock(false);
        });

        // triggers username input change to enable the verify button and click
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();

        // emit setVerifyResult will not be called, when prop domain is I, mock api returns user not found
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).not.toBeTruthy();

        const cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;
        expect(cardEl.textContent).toContain('Username');
        expect(wrapper.find('#userId').element.textContent).toContain(USERID);
        expect(wrapper.find('#userNotExist').element.textContent).toContain(
            'User does not exist'
        );
    });

    it('Should remove card and emit different value when domain changes', async () => {
        // show user identity card to prepare for the test
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();
        const cardUsernameEl = wrapper.find('.custom-card')
            .element as HTMLSpanElement;
        expect(cardUsernameEl).toBeTruthy();

        // change the domain to be B
        await wrapper.setProps({ domain: UserType.B });
        // for BCeID should emit true
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult![0][0]).toEqual(true);
        // UserIdentityCard not on page anymore
        expect(wrapper.findAll('#UserIdentityCard')).toHaveLength(0);

        // change the domain to be I
        await wrapper.setProps({ domain: UserType.I });
        // for IDIR should emit false
        expect(emitSetVerifyResult![1][0]).toEqual(false);
    });
});
