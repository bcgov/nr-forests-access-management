import { it, describe, beforeEach, expect} from 'vitest';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr()

describe('UserIdentityCard', () => {
    let wrapper: VueWrapper;

    let card: DOMWrapper<HTMLElement>;
    let cardEl: HTMLDivElement;
    let username: DOMWrapper<HTMLElement>;
    let usernameEl: HTMLSpanElement;

    const props = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: 'First Name',
            lastName: 'Last Name',
        },
    };

    const propsNotFound = {
        userIdentity: {
            userId: 'userId',
            found: false,
            firstName: null,
            lastName: null,
        },
    };

    beforeEach(async () => {
        wrapper = mount(UserIdentityCard, {
            props,
            global: {
                plugins: [PrimeVue],
            },
        });

        card = wrapper.find('.custom-card');
        cardEl = card.element as HTMLInputElement;
        username = wrapper.find('#userId');
        usernameEl = username.element as HTMLSpanElement;
    });

    it('Should show correct info on card based on props', () => {
        //it renders
        expect(wrapper.find('.custom-card').element).toBeTruthy();

        expect(usernameEl.textContent).toContain(props.userIdentity.userId);
        expect(wrapper.find('#firstName').element.textContent).toContain(props.userIdentity.firstName);
        expect(wrapper.find('#lastName').element.textContent).toContain(props.userIdentity.lastName);
        expect(wrapper.find('#checkmarkIcon')).toBeTruthy();
    });

    it('Should show the User does not exist when receive not found prop', async () => {
        await wrapper.setProps(propsNotFound);

        expect(usernameEl.textContent).toContain(propsNotFound.userIdentity.userId);
        expect(wrapper.find('#userNotExist').element.textContent).toContain('User does not exist');
        expect(wrapper.find('#errorIcon')).toBeTruthy();
    });
});
