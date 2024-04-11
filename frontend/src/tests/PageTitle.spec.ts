import PageTitle from '@/components/common/PageTitle.vue';
import router, { routes } from '@/router';
import { mount, VueWrapper } from '@vue/test-utils';
import { it, describe, beforeEach, expect, afterEach,vi } from 'vitest';
import { createRouter, createWebHistory, useRouter } from 'vue-router';
import { beforeEachRouteHandler } from '../router/routeHandlers';
import { routeItems } from '@/router/routeItem';
import { fixJsdomCssErr } from './common/fixJsdomCssErr';
import PrimeVue from 'primevue/config';

fixJsdomCssErr();
vi.mock('vue-router', async () => {
    const actual: Object = await vi.importActual("vue-router");
    return {
        ...actual,
        useRoute: () => {
            return routes.filter(
                (route) => route.name == routeItems.grantAppAdmin.name
            )[0]
        }
    };
});

describe('PageTitle', () => {
    let wrapper: VueWrapper;

    const props = {
        title: 'Header title',
        subtitle: 'Header subtitle',
    };

    beforeEach(async () => {
        wrapper = mount(PageTitle, {
            global: {
                plugins: [PrimeVue],
            },
            props
        });
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it('Should display the correct heading texts', () => {
        expect(wrapper.find(".title").element.textContent).toContain(
            props.title
        );

        expect(wrapper.find(".subtitle").element.textContent).toContain(
            props.subtitle
        );
    })

})