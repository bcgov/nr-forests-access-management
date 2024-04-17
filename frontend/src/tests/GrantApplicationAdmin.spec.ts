import { routes } from '@/router';
import { mount, VueWrapper } from '@vue/test-utils';
import { it, describe, beforeEach, expect, afterEach,vi } from 'vitest';
import { routeItems } from '@/router/routeItem';
import { fixJsdomCssErr } from './common/fixJsdomCssErr';
import GrantApplicationAdmin from '@/components/grantaccess/GrantApplicationAdmin.vue';

fixJsdomCssErr();
vi.mock('vue-router', async () => {
    const actual: Object = await vi.importActual('vue-router');
    return {
        ...actual,
        useRoute: () => {
            return routes.filter(
                (route) => route.name == routeItems.grantAppAdmin.name
            )[0];
        },
    };
});
describe('GrantApplicationAdmin', () => {
    let wrapper: VueWrapper;

    beforeEach(async () => {
        wrapper = mount(GrantApplicationAdmin);
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it('Should display the correct heading texts', () => {
        // console.log(wrapper.html())
        wrapper.findAll('.title').forEach((title) => {
            expect(title.isVisible()).toBe(true)
        })

        wrapper.findAll('.subtitle').forEach((subtitle) => {
            expect(subtitle.isVisible()).toBe(true)
        })
        expect(wrapper.find('#userIdInput').isVisible()).toBe(true)
        expect(wrapper.find('[aria-label="Verify user IDIR"]').isVisible()).toBe(true)
    })

})