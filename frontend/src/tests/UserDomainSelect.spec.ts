import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { UserType } from 'fam-app-acsctl-api';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr()

describe('UserDomainSelect', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;

    let bceidRadioBtn: DOMWrapper<HTMLInputElement>;
    let idirRadioBtn: DOMWrapper<HTMLInputElement>;

    beforeEach(async () => {
        wrapper = mount(UserDomainSelect);
        bceidRadioBtn = wrapper.find('#bceidSelect');
        idirRadioBtn = wrapper.find('#idirSelect');

    });

    it('Should check the radioBtn box when clicked', async () => {

        await bceidRadioBtn.trigger('click');
        expect(idirRadioBtn.element.checked).toBeFalsy();
        expect(bceidRadioBtn.element.checked).toBeTruthy();

        await idirRadioBtn.trigger('click');
        expect(bceidRadioBtn.element.checked).toBeFalsy();
        expect(idirRadioBtn.element.checked).toBeTruthy();

    });

    it('Should call and emit the correct value', async () => {
        await bceidRadioBtn.trigger('click');

        emitChange = wrapper.emitted('change');

        //expect emit has been called
        expect(wrapper.emitted()).toHaveProperty('change');

        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(emitChange![0][0]).toEqual(UserType.B);

        await idirRadioBtn.trigger('click');

        expect(emitChange![1][0]).toEqual(UserType.I);
    });

    it('Should receive the correct prop', async () => {
        expect(wrapper.props()).toEqual({ domain: UserType.I });

        await wrapper.setProps({ domain: UserType.B });

        expect(wrapper.props()).toEqual({ domain: UserType.B });
    });

    it('Should check the correct radioBtn based on the props', async () => {

        // start with IDIR checked
        expect(idirRadioBtn.element.checked).toBeTruthy();

        await wrapper.setProps({ domain: UserType.B });
        expect(bceidRadioBtn.element.checked).toBeTruthy();

        await wrapper.setProps({ domain: UserType.I });
        expect(idirRadioBtn.element.checked).toBeTruthy();
    });
});
