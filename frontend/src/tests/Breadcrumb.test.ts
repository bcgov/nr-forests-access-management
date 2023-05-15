import {
    flushPromises,
    mount,
    shallowMount,
    VueWrapper,
} from '@vue/test-utils';
import Breadcrumb from '@/components/Breadcrumb.vue';
import { it, describe, expect, beforeEach } from 'vitest';
import { routes } from '@/router';
import { createRouter, createWebHistory, type Router } from 'vue-router';
import {
    applicationsUserAdministers,
    selectedApplication,
} from '@/store/ApplicationState';
import type { FamApplication } from 'fam-api';
import type { Plugin } from 'vue';

describe('Breadcrumb Component', () => {
    let wrapper: VueWrapper;
    let router: Router;

    beforeEach(async () => {
        router = createRouter({
            history: createWebHistory(),
            routes: routes,
        });
        wrapper = mount(Breadcrumb, {
            global: {
                plugins: [router],
            },
        });
        await flushPromises();
    });

    it('should be blank when home page', async () => {
        router.push('/home');
        await flushPromises();
        expect(wrapper.html()).toEqual('<span></span>');
    });

    it('should not show SelectApplication when user can administer only one app', async () => {
        applicationsUserAdministers.value = [
            {
                application_name: 'FAKE',
                application_description: 'Fake Test App',
                application_id: 9999,
            },
        ] as FamApplication[];
        selectedApplication.value = applicationsUserAdministers.value[0];

        router.push('/manage');
        await flushPromises();
        expect(wrapper.html().includes('Select Application')).toBeFalsy();
    });

    it('should show SelectApplication when user can administer more than one app', async () => {
        applicationsUserAdministers.value = [
            {
                application_name: 'FAKE',
                application_description: 'Fake Test App',
                application_id: 9999,
            },
            {
                application_name: 'FAKE2',
                application_description: 'Fake 2 Test App',
                application_id: 9998,
            },
        ] as FamApplication[];
        selectedApplication.value = applicationsUserAdministers.value[0];

        router.push('/manage');
        await flushPromises();
        expect(wrapper.html().includes('Select Application')).toBeTruthy();
    });
});
