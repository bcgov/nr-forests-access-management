import GrantApplicationAdmin from "@/components/grantaccess/GrantApplicationAdmin.vue";
import { hashRouter, hashRoutes } from "@/router";
import { routeItems } from "@/router/RouteItems";
import { populateBreadcrumb } from "@/store/BreadcrumbState";
import { mount, VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import waitForExpect from "wait-for-expect";
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

describe("GrantApplicationAdmin", () => {
    let wrapper: VueWrapper;
    const routerPushSpy = vi.spyOn(hashRouter, "push");

    //populate the breadcrumbState
    const breadcrumbItems = [routeItems.dashboard];
    populateBreadcrumb(breadcrumbItems);
    beforeEach(async () => {
        wrapper = mount(GrantApplicationAdmin, {
            global: {
                plugins: [hashRouter], // Inject mocked Vue Router
            },
        });
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it("Should display the correct heading texts", () => {
        const titleText = [
            "Add application admin",
            "User information",
            "Add application",
        ];
        const subtitleText = [
            "All fields are mandatory",
            "Select an application this user will be able to manage",
        ];
        wrapper.findAll(".title").forEach((title, i) => {
            expect(title.isVisible()).toBe(true);
            expect(title.element.textContent).toContain(titleText[i]);
        });

        wrapper.findAll(".subtitle").forEach((subtitle, i) => {
            expect(subtitle.isVisible()).toBe(true);
            expect(subtitle.element.textContent).toContain(subtitleText[i]);
        });
    });

    it("Should display the correct breadcrumb info", async () => {
        const breadcrumb = wrapper.findComponent({ name: "Breadcrumb" });

        expect(breadcrumb.exists()).toBe(true);

        // assert that primevue breadcrumb is receiving the correct prop
        expect(breadcrumb.props("model")).toEqual(breadcrumbItems);

        // assert that the text is the same as the breacrumbItems label
        breadcrumb
            .findAll("p-breadcrumb-list span")
            .forEach((breadcrumbItem, i) => {
                expect(breadcrumbItem.isVisible()).toBe(true);
                expect(breadcrumbItem.element.textContent).toBe(
                    breadcrumbItems[i].label
                );
            });
    });

    it("Should redirect when breadcrumb item is clickled", async () => {
        const breadcrumb = wrapper.findComponent({ name: "Breadcrumb" });
        const breadcrumbDashboardItem = breadcrumb.findAll("a").find((item) => {
            return item.element.textContent === routeItems.dashboard.label;
        });

        expect(breadcrumbDashboardItem?.element.textContent).toBe(
            routeItems.dashboard.label
        );
        await breadcrumbDashboardItem?.trigger("click");
        expect(routerPushSpy).toHaveBeenCalledWith(routeItems.dashboard.path);
    });

    it("Should show validation error when username input invalid", async () => {
        const usernameInputText = wrapper.find("#userIdInput");
        const usernameInputTextEl =
            usernameInputText.element as HTMLInputElement;
        const btnVerify = wrapper.find(".input-with-verify-button button");

        // input is rendered
        expect(usernameInputText.isVisible()).toBe(true);
        expect(btnVerify.isVisible()).toBe(true);

        //verify btn is disabled by default
        expect((btnVerify.element as HTMLButtonElement).disabled).toBe(true);
        expect(btnVerify.classes()).toContain("p-disabled");

        await usernameInputText.setValue("I");
        expect(usernameInputTextEl.value).toBe("I");

        await waitForExpect(() => {
            expect(
                wrapper.find(".input-with-verify-button .invalid-feedback")
                    .element.textContent
            ).toContain("at least 2 characters");

            //verify btn is disabled
            expect((btnVerify.element as HTMLButtonElement).disabled).toBe(
                true
            );
            expect(btnVerify.classes()).toContain("p-disabled");
        });

        await usernameInputText.setValue("");

        expect(usernameInputTextEl.value).toBe("");
        await waitForExpect(() => {
            expect(
                wrapper.find(".input-with-verify-button .invalid-feedback")
                    .element.textContent
            ).toContain("required");

            //verify btn is disabled
            expect((btnVerify.element as HTMLButtonElement).disabled).toBe(
                true
            );
            expect(btnVerify.classes()).toContain("p-disabled");
        });
    });

    it("Should call cancelForm method and route to dashboard", async () => {
        // Spy on cancelForm method, spy on hashRouter.push
        const cancelFormSpy = vi.spyOn(wrapper.vm as any, "cancelForm");
        const cancelBtn = wrapper.get("#grantAdminCancel");

        await cancelBtn.trigger("click");

        // cancelForm is called
        expect(cancelFormSpy).toHaveBeenCalled();
        // called route.push with '/dashboard'
        expect(routerPushSpy).toHaveBeenCalledWith(routeItems.dashboard.path);
    });

    it("Should render submit btn and disabled by default", () => {
        const submitBtn = wrapper.find("#grantAdminSubmit");
        expect(submitBtn.isVisible()).toBe(true);
        expect((submitBtn.element as HTMLButtonElement).disabled).toBe(true);
        expect(submitBtn.classes()).toContain("p-disabled");
    });
});
