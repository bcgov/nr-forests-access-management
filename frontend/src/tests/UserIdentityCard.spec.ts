import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr();

describe('UserIdentityCard', () => {
    let wrapper: VueWrapper;

    const propsIDIR = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: 'First Name',
            lastName: 'Last Name',
        },
        errorMsg: '',
    };

    const propsBusinessBCeID = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: 'First Name',
            lastName: 'Last Name',
            businessLegalName: 'Business Name',
        },
        errorMsg: '',
    };

    const propsNotFound = {
        userIdentity: {
            userId: 'userId',
            found: false,
        },
        errorMsg: '',
    };

    const propsPermissionError = {
        userIdentity: {
            userId: 'userId',
            found: false,
        },
        errorMsg: 'test permission error messages',
    };

    beforeEach(async () => {
        wrapper = mount(UserIdentityCard, { props: propsIDIR });
    });

    it('Should show correct user info on card when receive IDIR identity in props', () => {
        expect(wrapper.find('.custom-card').element).toBeTruthy();
        expect(wrapper.find('.custom-card').element.textContent).toContain(
            'Verified user information'
        );
        expect(wrapper.find('#userId').element.textContent).toContain(
            propsIDIR.userIdentity.userId
        );
        expect(wrapper.find('#firstName').element.textContent).toContain(
            propsIDIR.userIdentity.firstName
        );
        expect(wrapper.find('#lastName').element.textContent).toContain(
            propsIDIR.userIdentity.lastName
        );
        expect(wrapper.find('#checkmarkIcon')).toBeTruthy();
    });

    it('Should show correct user info on card when receive Business BCeID identity in props', async () => {
        await wrapper.setProps(propsBusinessBCeID);
        expect(wrapper.find('.custom-card').element.textContent).toContain(
            'Verified user information'
        );
        expect(wrapper.find('#userId').element.textContent).toContain(
            propsBusinessBCeID.userIdentity.userId
        );
        expect(wrapper.find('#firstName').element.textContent).toContain(
            propsBusinessBCeID.userIdentity.firstName
        );
        expect(wrapper.find('#lastName').element.textContent).toContain(
            propsBusinessBCeID.userIdentity.lastName
        );
        expect(wrapper.find('#organizationName').element.textContent).toContain(
            propsBusinessBCeID.userIdentity.businessLegalName
        );
        expect(wrapper.find('#checkmarkIcon')).toBeTruthy();
    });

    it('Should show the user does not exist when receive not found in props', async () => {
        await wrapper.setProps(propsNotFound);
        expect(wrapper.find('.custom-card').element.textContent).toContain(
            'Verified user information'
        );
        expect(wrapper.find('#userId').element.textContent).toContain(
            propsNotFound.userIdentity.userId
        );
        expect(wrapper.find('#userNotExist').element.textContent).toContain(
            'User does not exist'
        );
        expect(wrapper.find('#errorIcon')).toBeTruthy();
    });

    it('Should display permission error messages if received in props', async () => {
        await wrapper.setProps(propsPermissionError);
        expect(wrapper.find('.custom-card').element.textContent).toContain(
            'Verified user information'
        );
        expect(wrapper.find('#errorMsg').element.textContent).toContain(
            propsPermissionError.errorMsg
        );
        expect(wrapper.find('#errorIcon')).toBeTruthy();
    });
});
