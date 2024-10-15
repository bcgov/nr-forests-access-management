import { it, describe, beforeEach, expect, vi } from "vitest";
import { flushPromises, shallowMount } from "@vue/test-utils";
import type { VueWrapper } from "@vue/test-utils/dist/vueWrapper";
import Landing from "@/components/Landing.vue";
import { Amplify } from "aws-amplify";
import AuthService from "@/services/AuthService";

describe("Landing", () => {
    let wrapper: VueWrapper;

    // TODO beforeEach(async () => {
    //     wrapper = shallowMount(Landing);
    //     vi.mock('aws-amplify');
    //     // Random values to mock
    //     Amplify.configure({
    //         Auth: {
    //             identityPoolId: 'abc',
    //             region: 'def',
    //             userPoolId: 'ghi',
    //             userPoolWebClientId: 'jkl',
    //         },
    //     });
    //     await flushPromises();
    // });
    // it('should render bc logo image', () => {
    //     const img = wrapper.findAll('.logo');
    //     expect(img.length).toBe(1);
    // });
    // it('should render title with correct class', () => {
    //     const element = wrapper.get('#landing-title');
    //     expect(element.text()).toEqual('Welcome to FAM');
    //     expect(element.classes()).toEqual(
    //         expect.arrayContaining(['landing-title'])
    //     );
    // });
    // it('should render subtitle with correct class', () => {
    //     const element = wrapper.get('#landing-subtitle');
    //     expect(element.text()).toEqual('Forests Access Management');
    //     expect(element.classes()).toEqual(
    //         expect.arrayContaining(['landing-subtitle'])
    //     );
    // });
    // it('should render description with correct class', () => {
    //     const element = wrapper.get('#landing-desc');
    //     expect(element.text()).toEqual('Grant access to your users');
    //     expect(element.classes()).toEqual(
    //         expect.arrayContaining(['landing-desc'])
    //     );
    // });
    // it('should render IDIR button and be enabled', () => {
    //     const button = wrapper.get('#login-idir-button');
    //     expect(button.classes()).toEqual(
    //         expect.arrayContaining(['landing-button'])
    //     );
    //     expect(button.html().includes('Login with IDIR')).toBe(true);
    //     expect(button.attributes()).not.toHaveProperty('disabled');
    // });
    // it('should button Login with IDIR be clicked', async () => {
    //     const button = wrapper.get('#login-idir-button');
    //     const loginSpy = vi.spyOn(AuthService, 'login');
    //     await button.trigger('click');
    //     expect(loginSpy).toHaveBeenCalled();
    // });
    it.skip("should render Business BCeID button and be enabled", async () => {
        const button = wrapper.get("#login-business-bceid-button");
        expect(button.classes()).toEqual(
            expect.arrayContaining(["landing-button"])
        );
        expect(button.html().includes("Login with Business BCeID")).toBe(true);
        expect(button.attributes()).not.toHaveProperty("disabled");
    });
    it.skip("should button Login with Business BCeID be clicked", async () => {
        const button = wrapper.get("#login-business-bceid-button");
        const loginSpy = vi.spyOn(AuthService, "loginBusinessBceid");
        await button.trigger("click");
        expect(loginSpy).toHaveBeenCalled();
    });
    it("should render image", () => {
        const img = wrapper.findAll(".landing-img");
        expect(img.length).toBe(1);
    });
});
