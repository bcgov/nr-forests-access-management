import { it, describe, beforeEach, afterEach, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { UserType } from 'fam-app-acsctl-api';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import UserNameInput from '@/components/grantaccess/form/UserNameInput.vue';
import { isLoading, setLoadingState } from '@/store/LoadingState';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import type { AxiosResponse } from 'axios';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';

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

const userInputMock = (
    userId: string,
    found: boolean
    ): AxiosResponse => {
        if(!found) {
            return {
                data: {
                    firstName: null,
                    found: found,
                    lastName: null,
                    userId: userId
                },
                status: 200,
                statusText: 'Ok',
                headers: {},
                config: {},
            }
        } else {
            return {
                data: {
                    firstName: "First Name",
                    found: found,
                    lastName: "Last Name",
                    userId: userId
                },
                status: 200,
                statusText: 'Ok',
                headers: {},
                config: {},
            }
        }

}
describe('UserNameInput', () => {
    let wrapper: VueWrapper;

    let card: DOMWrapper<HTMLElement>
    let cardEl: HTMLDivElement
    let username: DOMWrapper<HTMLElement>
    let usernameEl: HTMLSpanElement
    let firstName: DOMWrapper<HTMLElement>
    let firstNameEl: HTMLSpanElement
    let lastName: DOMWrapper<HTMLElement>
    let lastNameEl: HTMLSpanElement
    let checkmarkIcon: DOMWrapper<SVGImageElement>
    let checkmarkIconEl: SVGImageElement


    const props = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: 'First Name',
            lastName: 'Last Name'
        }
    }

    const propsNotFound = {
        userIdentity: {
            userId: 'userId',
            found: true,
            firstName: null,
            lastName: null
        }
    }

    beforeEach(async () => {
        wrapper = mount(UserIdentityCard, {
            props,
            global: {
                plugins: [PrimeVue],
            },
        });

        card = wrapper.find('.custom-card');
        cardEl = card.element as HTMLInputElement;
        username = wrapper.find("#username");
        usernameEl = username.element as HTMLSpanElement
        firstName = wrapper.find("#firstName");
        firstNameEl = firstName.element as HTMLSpanElement
        lastName = wrapper.find("#lastName");
        lastNameEl = lastName.element as HTMLSpanElement
        checkmarkIcon = wrapper.find('#checkmark-Icon');
        // checkmarkIconEl = checkmarkIcon.element as SVGImageElement

    });

    it('Should show correct info on card based on props', async () => {
        //it renders
        expect(card.element).toBeTruthy()

        expect(usernameEl.textContent).toContain(props.userIdentity.userId);
        expect(firstNameEl.textContent).toContain(props.userIdentity.firstName);
        expect(lastNameEl.textContent).toContain(props.userIdentity.lastName);
        expect(checkmarkIcon).toBeTruthy();
    });

    // it()

})