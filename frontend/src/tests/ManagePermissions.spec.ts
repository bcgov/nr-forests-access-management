import ManagePermissions from '@/components/managePermissions/ManagePermissions.vue';
import { routes } from '@/router';
import { routeItems } from '@/router/routeItem';
import FamLoginUserState from '@/store/FamLoginUserState';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';
import { DOMWrapper, mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import PrimeVue from 'primevue/config';
import { afterEach, beforeEach, describe, expect, it, vi, type SpyInstance } from 'vitest';
import { nextTick } from 'vue';

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
        let getUserAccessSpy: SpyInstance;
        let appDropdownInput: DOMWrapper<HTMLInputElement>;
        let appDropdownButtonDiv: DOMWrapper<HTMLInputElement>;

        beforeEach(async () => {
            getUserAccessSpy = vi.spyOn(FamLoginUserState,'getUserAccess');
            wrapper = mount(ManagePermissions, {
                global: {
                    plugins: [PrimeVue] // need this from PrimeVue to prevent config error.
                }
            });
            appDropdownInput = wrapper.find(appDropdownIdSelector);
            // select direct sibling <div> to be trigger
            appDropdownButtonDiv = wrapper.find(appDropdownIdSelector + " + div");

        });

        it("should be empty when user has no admin privilege", async () => {
            // No available options mock: for user who has no privilege.
            getUserAccessSpy.mockImplementation(() => []);

            // Initial apps dropdown verify.
            expect(wrapper.text()).contains("Choose an application to manage permissions");
            expect(appDropdownInput.exists()).toBe(true);
            expect(appDropdownButtonDiv.exists()).toBe(true);
            expect(wrapper.text()).not.contains("No available options");

            await appDropdownButtonDiv.trigger('click');
            await nextTick();
        });

        afterEach(async () => {
            wrapper.unmount();
        })
    });
});

const famAccessMock = [
    {
       "auth_key": "FAM_ADMIN",
       "grants": [
          {
             "application": {
                "id": 1,
                "name": "FAM",
                "description": "Forests Access Management",
                "env": null
             },
             "roles": null
          },
          {
             "application": {
                "id": 2,
                "name": "FOM",
                "description": "Forest Operations Map (DEV)",
                "env": "DEV"
             },
             "roles": null
          },
          {
             "application": {
                "id": 3,
                "name": "FOM",
                "description": "Forest Operations Map (TEST)",
                "env": "TEST"
             },
             "roles": null
          },
          {
             "application": {
                "id": 4,
                "name": "FOM",
                "description": "Forest Operations Map (PROD)",
                "env": "PROD"
             },
             "roles": null
          },
          {
             "application": {
                "id": 5,
                "name": "SPAR",
                "description": "Seed Planning and Registry Application (DEV)",
                "env": "DEV"
             },
             "roles": null
          },
          {
             "application": {
                "id": 6,
                "name": "SPAR",
                "description": "Seed Planning and Registry Application (TEST)",
                "env": "TEST"
             },
             "roles": null
          },
          {
             "application": {
                "id": 7,
                "name": "SPA",
                "description": "Seed Planning and Registry Application (PROD)",
                "env": "PROD"
             },
             "roles": null
          },
          {
             "application": {
                "id": 8,
                "name": "CLIENT",
                "description": "Forest Client (DEV)",
                "env": "DEV"
             },
             "roles": null
          },
          {
             "application": {
                "id": 9,
                "name": "CLIEN",
                "description": "Forest Client (TEST)",
                "env": "TEST"
             },
             "roles": null
          },
          {
             "application": {
                "id": 10,
                "name": "CLIENT",
                "description": "Forest Client (PROD)",
                "env": "PROD"
             },
             "roles": null
          },
          {
             "application": {
                "id": 11,
                "name": "SILVA",
                "description": "SILVA (DEV)",
                "env": "DEV"
             },
             "roles": null
          },
          {
             "application": {
                "id": 12,
                "name": "SILVA",
                "description": "SILVA (TEST)",
                "env": "TEST"
             },
             "roles": null
          },
          {
             "application": {
                "id": 13,
                "name": "SILVA",
                "description": "SILVA (PROD)",
                "env": "PROD"
             },
             "roles": null
          }
       ]
    }
 ];