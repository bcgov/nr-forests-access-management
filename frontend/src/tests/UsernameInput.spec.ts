import { it, describe, beforeAll, beforeEach, afterEach, expect, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosRequestHeaders, AxiosResponse, AxiosError } from 'axios';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';
import FamLoginUserState from '@/store/FamLoginUserState';
import { UserType } from 'fam-admin-mgmt-api/model';

fixJsdomCssErr();

const USERID = 'TestUser';
const FIRSTNAME = 'TestUserFirstName';
const LASTNAME = 'TestUserLastName';
const BUSINESSLEGALNAME = 'TestBusinessLegalName';
const TESTUSERGUID = '00000000000000000000000000000000';
const IDPPROVIDERIDIR =  'idpTest-BCEIDBUSINESS'
const IDPPROVIDERBCEID = 'idpTest-IDIR'
const NOT_SAME_ORG_ERROR_MSG = 'Operation requires business bceid users to be within the same organization'

const idimIdirSearchMock = (isUserFound: boolean): AxiosResponse => {
    if (isUserFound) {
        return {
            data: {
                firstName: FIRSTNAME,
                found: true,
                lastName: LASTNAME,
                userId: USERID,
                guid: TESTUSERGUID, // no need to pass a real guid here
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

const idimBceidSearchMock = (
    isUserFound: boolean,
    isPermissionError: boolean = false,
): AxiosResponse | AxiosError => {
    if (isUserFound) {
        return {
            data: {
                found: true,
                userId: USERID,
                firstName: FIRSTNAME,
                lastName: LASTNAME,
                businessLegalName: BUSINESSLEGALNAME,
                businessGuid: '', // no need to pass a real guid here
                guid: TESTUSERGUID, // no need to pass a real guid here
            },
            status: 200,
            statusText: 'Ok',
            headers: {},
            config: {
                headers: {} as AxiosRequestHeaders,
            },
        };
    } else if (isPermissionError) {
            throw {
                code: 'ERR_BAD_REQUEST',
                response: {
                    data: {
                        detail: {
                            code: 'permission_required_for_operation',
                            description: NOT_SAME_ORG_ERROR_MSG,
                        },
                    },
                    status: 403,
                },
            }
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

const mockFamLoginUser = (userType: UserType) => {
    return {
        username: 'usernameTEST',
        displayName: 'displayNameTest',
        email: 'email_test@test.com',
        idpProvider: UserType.I ? IDPPROVIDERIDIR : IDPPROVIDERBCEID,
        organization: 'organizationTest',
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

    beforeAll(() => {
        // we need to set the FamLoginUser as the error message uses famLoginUser.organization
        FamLoginUserState.storeFamUser(mockFamLoginUser(UserType.I));
    });

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
        // for BCeID should emit false
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult![0][0]).toEqual(false);
        // UserIdentityCard not on page anymore
        expect(wrapper.findAll('#UserIdentityCard')).toHaveLength(0);

        // change the domain to be I
        await wrapper.setProps({ domain: UserType.I });
        // for IDIR should emit false
        expect(emitSetVerifyResult![1][0]).toEqual(false);
    });

    //-------- idir domain tests
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

    it('Should show the user identity card with correct info when IDIR user is found', async () => {
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

        // call emit setVerifyResult with true, mock api returns user found
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).toBeTruthy();
        expect(emitSetVerifyResult![0][0]).toEqual(true);
        expect(emitSetVerifyResult![0][1]).toEqual(TESTUSERGUID);

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

    //-------- BCEID domain tests
    it('Should show the user identity card with correct info when BCEID user is found', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'bceidSearch'
        ).mockImplementation(async () => {
            return idimBceidSearchMock(true) as AxiosResponse;
        });

        // by default no identity card display
        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(false);

        // triggers username input change to enable the verify button and click
        await wrapper.setProps({ domain: UserType.B });
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();

        // call emit setVerifyResult with true, mock api returns user found
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).toBeTruthy();
        // i.e. emitSetVerifyResult = [ [ false ], [ true, '' ] ]
        // the outter array indicates how many times it has been called
        // the inner array indicates how many parameters it has
        // when we call wrapper.setProps({ domain: UserType.B }) above, the emitSetVerifyResult already be called once with parameter false
        expect(emitSetVerifyResult![1][0]).toEqual(true);
        expect(emitSetVerifyResult![1][1]).toEqual(TESTUSERGUID);

        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(true);
        const cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;
        // verify identity card title
        expect(cardEl.textContent).toContain('Username');
        expect(cardEl.textContent).toContain('First Name');
        expect(cardEl.textContent).toContain('Last Name');
        expect(cardEl.textContent).toContain('Organization Name');
        // verify identity card user info
        expect(wrapper.find('#userId').element.textContent).toContain(USERID);
        expect(wrapper.find('#firstName').element.textContent).toContain(
            FIRSTNAME
        );
        expect(wrapper.find('#lastName').element.textContent).toContain(
            LASTNAME
        );
        expect(wrapper.find('#organizationName').element.textContent).toContain(
            BUSINESSLEGALNAME
        );
    });

    it('should BCeID user able to verify other BCeID users and display info on card', async() => {
        // Mock successful BCeID user search
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'bceidSearch'
        ).mockImplementation(async () => {
            return idimBceidSearchMock(true) as AxiosResponse;
        });

        // Set initial props for a Business BCeID user
        await wrapper.setProps({ domain: UserType.B, userId: USERID });

        // Verify the button is enabled
        expect(verifyButtonEl.disabled).toBe(false);
        expect(verifyButton.classes('p-disabled')).toBe(false);

        // Click the verify button and wait for promises to resolve
        await verifyButton.trigger('click');
        await flushPromises();

        // Verify the UserIdentityCard component is displayed with correct user info
        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(true);
        const cardEl = wrapper.find('.custom-card').element as HTMLSpanElement;

        // Verify identity card details
        expect(cardEl.textContent).toContain('Username');
        expect(cardEl.textContent).toContain('First Name');
        expect(cardEl.textContent).toContain('Last Name');
        expect(cardEl.textContent).toContain('Organization Name');

        // Verify user info in the card
        expect(wrapper.find('#userId').element.textContent).toContain(USERID);
        expect(wrapper.find('#firstName').element.textContent).toContain(FIRSTNAME);
        expect(wrapper.find('#lastName').element.textContent).toContain(LASTNAME);
        expect(wrapper.find('#organizationName').element.textContent).toContain(BUSINESSLEGALNAME);
    });

    it('Should show the user identity card error msg when BCEID user is not the same org', async () => {
        vi.spyOn(
            AppActlApiService.idirBceidProxyApi,
            'bceidSearch'
        ).mockImplementation(async () => {
            return idimBceidSearchMock(false, true) as AxiosResponse;
        });

        // by default no identity card display
        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(false);

        // triggers username input change to enable the verify button and click
        await wrapper.setProps({ domain: UserType.B });
        await wrapper.setProps({ userId: USERID });
        await verifyButton.trigger('click');
        await flushPromises();

        // call emit setVerifyResult with true, mock api returns permission error, won't call setVerifyResult
        const emitSetVerifyResult = wrapper.emitted('setVerifyResult');
        expect(emitSetVerifyResult).toBeTruthy();
        // setVerifyResult is only called once when we call wrapper.setProps({ domain: UserType.B }) above
        // when we verify the business bceid user but got a permission error, won't call emitSetVerifyResult again
        expect(emitSetVerifyResult!.length).toEqual(1);

        expect(wrapper.findComponent(UserIdentityCard).exists()).toBe(true);
        expect(wrapper.find('#errorMsg').exists()).toBe(true);
        expect(wrapper.find('#errorMsg').element.textContent).toContain(NOT_SAME_ORG_ERROR_MSG);
        console.log(wrapper.html())
    });

});
