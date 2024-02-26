import ManagePermissions from '@/components/managePermissions/ManagePermissions.vue';
import { routes } from '@/router';
import { routeItems } from '@/router/routeItem';
import FamLoginUserState from '@/store/FamLoginUserState';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';
import { DOMWrapper, mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import { afterEach, beforeEach, describe, expect, it, vi, type SpyInstance } from 'vitest';

fixJsdomCssErr();

// router mock setup (for mounting component properly when involving other components)
vi.mock('vue-router', async () => {
    const actual: Object = await vi.importActual("vue-router");
    return {
        ...actual,
        useRoute: () => {
            return routes.filter(
                (route) => route.name == routeItems.dashboard.name
            )[0]
        }
    };
});

describe('ManagePermissions', () => {
    let wrapper: VueWrapper;

    describe('Application dropdown selection', () => {
        const appDropdownIdSelector = "#applications-dropdown-id";
        let getuserAccessSpy: SpyInstance;
        let appDropdownInput: DOMWrapper<HTMLInputElement>;
        let appDropdownButtonDiv: DOMWrapper<HTMLInputElement>;

        beforeEach(async () => {
            getuserAccessSpy = vi.spyOn(FamLoginUserState,'getUserAccess');
            wrapper = mount(ManagePermissions);
            appDropdownInput = wrapper.find(appDropdownIdSelector);
            appDropdownButtonDiv = wrapper.find(appDropdownIdSelector + " + div");
        });

        it("should be empty when user access state is empty", async () => {
            // No available options
            getuserAccessSpy.mockImplementation(() => []);
            expect(wrapper.text()).contains("Choose an application to manage permissions");
            expect(appDropdownInput.exists()).toBe(true);
            expect(appDropdownButtonDiv.exists()).toBe(true);
            expect(wrapper.text()).not.contains("No available options");
        });

        afterEach(async () => {
            wrapper.unmount();
        })
    });
});