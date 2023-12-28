import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { UserType } from 'fam-app-acsctl-api';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';

describe('UserDomainSelect', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;

    let becidRadioBtn: DOMWrapper<HTMLInputElement>;
    let idirRadioBtn: DOMWrapper<HTMLInputElement>;

    beforeEach(async () => {
        wrapper = mount(UserDomainSelect);
        becidRadioBtn = wrapper.find('#becidSelect');
        idirRadioBtn = wrapper.find('#idirSelect');

    });

    it('Should check the radioBtn box when clicked', async () => {

        await becidRadioBtn.trigger('click');
        expect(becidRadioBtn.element.checked).toBeTruthy();

        await idirRadioBtn.trigger('click');
        expect(idirRadioBtn.element.checked).toBeTruthy();

    });

    it('Should call and emit the correct value', async () => {
        await becidRadioBtn.trigger('click');

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
        expect(becidRadioBtn.element.checked).toBeTruthy();

        await wrapper.setProps({ domain: UserType.I });
        expect(idirRadioBtn.element.checked).toBeTruthy();
    });
});
