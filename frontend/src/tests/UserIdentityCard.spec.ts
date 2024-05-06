import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr();

describe('UserIdentityCard', () => {
    let wrapper: VueWrapper;

    const props = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: 'First Name',
            lastName: 'Last Name',
        },
        errorMgs: ''
    };

    const propsNotFound = {
        userIdentity: {
            userId: 'userId',
            found: false,
        },
        errorMgs: ''
    };

    beforeEach(async () => {
        wrapper = mount(UserIdentityCard, { props });
    });

    it('Should show correct user info on card when receive identity in prop', () => {
        expect(wrapper.find('.custom-card').element).toBeTruthy();
        expect(wrapper.find('.custom-card').element.textContent).toContain(
            'Verified user information'
        );
        expect(wrapper.find('#userId').element.textContent).toContain(
            props.userIdentity.userId
        );
        expect(wrapper.find('#firstName').element.textContent).toContain(
            props.userIdentity.firstName
        );
        expect(wrapper.find('#lastName').element.textContent).toContain(
            props.userIdentity.lastName
        );
        expect(wrapper.find('#checkmarkIcon')).toBeTruthy();
    });

    it('Should show the user does not exist when receive not found in prop', async () => {
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
});
