import router, { routes } from '@/router';
import { mount, RouterLinkStub, VueWrapper } from '@vue/test-utils';
import { it, describe, beforeEach, expect, afterEach, vi } from 'vitest';
import { routeItems } from '@/router/routeItem';
import { fixJsdomCssErr } from './common/fixJsdomCssErr';
import GrantApplicationAdmin from '@/components/grantaccess/GrantApplicationAdmin.vue';
import waitForExpect from 'wait-for-expect';

fixJsdomCssErr();
const mockRoutePush = vi.fn();
vi.mock('vue-router', async () => {
    const actual: Object = await vi.importActual('vue-router');
    return {
        ...actual,
        useRoute: () => {
            return routes.filter(
                (route) => route.name == routeItems.grantAppAdmin.name
            )[0];
        },
        useRouter: () => {
            return {
                push: mockRoutePush,
            };
        },
    };
});

describe('GrantApplicationAdmin', () => {
    let wrapper: VueWrapper;

    beforeEach(async () => {
        wrapper = mount(GrantApplicationAdmin, {
            global: {
                components: {
                    RouterLink: RouterLinkStub, // Stub RouterLink component
                },
                mocks: {
                    $router: {
                        push: vi.fn(),
                    },
                },
            },
        });
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it('Should display the correct heading texts', () => {
        // console.log(wrapper.html())
        const titleText = [
            'Add application admin',
            'User information',
            'Add application',
        ];
        const subtitleText = [
            'All fields are mandatory',
            'Select an application this user will be able to manage',
        ];
        wrapper.findAll('.title').forEach((title, i) => {
            expect(title.isVisible()).toBe(true);
            expect(title.element.textContent).toContain(titleText[i]);
        });

        wrapper.findAll('.subtitle').forEach((subtitle, i) => {
            expect(subtitle.isVisible()).toBe(true);
            expect(subtitle.element.textContent).toContain(subtitleText[i]);
        });
        expect(wrapper.find('#userIdInput').isVisible()).toBe(true);
        expect(
            wrapper.find('[aria-label="Verify user IDIR"]').isVisible()
        ).toBe(true);
        expect(
            wrapper.find('.application-admin-group .p-dropdown').isVisible()
        ).toBe(true);

        // console.log(wrapper.html())
    });

    it('Should show validation error when username input invalid', async () => {
        const usernameInputText = wrapper.find('#userIdInput');
        const usernameInputTextEl =
            usernameInputText.element as HTMLInputElement;

        await usernameInputText.setValue('I');
        expect(usernameInputTextEl.value).toBe('I');

        await waitForExpect(() => {
            expect(
                wrapper.find('.input-with-verify-button .invalid-feedback')
                    .element.textContent
            ).toContain('at least 2 characters');

            //verify btn is disabled
            expect(
                wrapper
                    .find('.input-with-verify-button button')
                    .classes('p-disabled')
            ).toBe(true);
        });

        await usernameInputText.setValue('');

        expect(usernameInputTextEl.value).toBe('');
        await waitForExpect(() => {
            expect(
                wrapper.find('.input-with-verify-button .invalid-feedback')
                    .element.textContent
            ).toContain('required');

            expect(
                wrapper
                    .find('.input-with-verify-button button')
                    .classes('p-disabled')
            ).toBe(true);
        });
    });

    it('Should call cancelForm method and route to dashboard', async () => {
        // Spy on cancelForm method
        const cancelFormSpy = vi.spyOn(wrapper.vm as any, 'cancelForm');
        const routerPushSpy = vi.spyOn(router, 'push');

        const cancelBtn = wrapper.get('#grantAdminCancel');
        await cancelBtn.trigger('click');

        // cancelForm is called
        expect(cancelFormSpy).toHaveBeenCalled();
        // called route.push with '/dashboard'
        expect(routerPushSpy).toHaveBeenCalledWith('/dashboard');
    });

    it('Should call cancelForm method and route to dashboard', async () => {
        // Spy on cancelForm method
        const cancelFormSpy = vi.spyOn(wrapper.vm as any, 'cancelForm');
        const routerPushSpy = vi.spyOn(router, 'push');

        const cancelBtn = wrapper.get('#grantAdminCancel');
        await cancelBtn.trigger('click');

        // cancelForm is called
        expect(cancelFormSpy).toHaveBeenCalled();
        // called route.push with '/dashboard'
        expect(routerPushSpy).toHaveBeenCalledWith('/dashboard');
    });

    it('should breadcrumb', () => {
        // console.log(wrapper.html())
    });
});
