import PageTitle from "@/components/common/PageTitle.vue";
import { hashRoutes } from "@/router";
import { mount, VueWrapper } from "@vue/test-utils";
import { it, describe, beforeEach, expect, afterEach, vi } from "vitest";
import { routeItems } from "@/router/RouteItems";
import { fixJsdomCssErr } from "./common/fixJsdomCssErr";

fixJsdomCssErr();
vi.mock("vue-router", async () => {
    const actual: Object = await vi.importActual("vue-router");
    return {
        ...actual,
        useRoute: () => {
            return hashRoutes.filter(
                (route) => route.name == routeItems.grantAppAdmin.name
            )[0];
        },
    };
});

describe("PageTitle", () => {
    let wrapper: VueWrapper;

    const props = {
        title: "Header title",
        subtitle: "Header subtitle",
    };

    beforeEach(async () => {
        wrapper = mount(PageTitle, {
            props,
        });
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it("Should display the correct heading texts", () => {
        expect(wrapper.find(".title").element.textContent).toContain(
            props.title
        );

        expect(wrapper.find(".subtitle").element.textContent).toContain(
            props.subtitle
        );
    });

    it("Should display breadcrumb", async () => {
        const breadcrumb = wrapper.findComponent({ name: "Breadcrumb" });
        expect(breadcrumb.exists()).toBe(true);
    });
});
