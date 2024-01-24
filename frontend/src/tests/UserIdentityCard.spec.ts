import { it, describe, beforeEach, expect} from 'vitest';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { fixPrimevueCssError } from '@/tests/common/fixPrimevueCssErr';

fixPrimevueCssError()

describe('UserIdentityCard', () => {
    let wrapper: VueWrapper;

    let card: DOMWrapper<HTMLElement>;
    let cardEl: HTMLDivElement;
    let username: DOMWrapper<HTMLElement>;
    let usernameEl: HTMLSpanElement;
    let firstName: DOMWrapper<HTMLElement>;
    let firstNameEl: HTMLSpanElement;
    let lastName: DOMWrapper<HTMLElement>;
    let lastNameEl: HTMLSpanElement;
    let userNotExist: DOMWrapper<HTMLElement>;
    let userNotExistEl: HTMLSpanElement;
    let checkmarkIcon: DOMWrapper<SVGImageElement>;
    let errorIcon: DOMWrapper<SVGImageElement>;

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
        firstName = wrapper.find('#firstName');
        firstNameEl = firstName.element as HTMLSpanElement;
        lastName = wrapper.find('#lastName');
        lastNameEl = lastName.element as HTMLSpanElement;
        checkmarkIcon = wrapper.find('#checkmark-Icon');
        errorIcon = wrapper.find('#error-icon');
    });

    it('Should show correct info on card based on props', () => {
        //it renders
        expect(card.element).toBeTruthy();

        expect(usernameEl.textContent).toContain(props.userIdentity.userId);
        expect(firstNameEl.textContent).toContain(props.userIdentity.firstName);
        expect(lastNameEl.textContent).toContain(props.userIdentity.lastName);
        expect(checkmarkIcon).toBeTruthy();
    });

    it('Should show the User does not exist when receive not found prop', async () => {
        await wrapper.setProps(propsNotFound);
        userNotExist = wrapper.find('#userNotExist');
        userNotExistEl = userNotExist.element as HTMLSpanElement;

        expect(usernameEl.textContent).toContain(propsNotFound.userIdentity.userId);
        expect(userNotExistEl.textContent).toContain('User does not exist');
        expect(errorIcon).toBeTruthy();
    });
});
