import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import { UserType } from 'fam-app-acsctl-api';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';

describe('UserDomainSelect', () => {
    let wrapper: VueWrapper;
    let emitChange: unknown[][] | undefined;
    let bceidInput: DOMWrapper<HTMLDivElement>;
    let idirInput: DOMWrapper<HTMLDivElement>;

    // primevue radio component have the check box on a div
    let idirRadioBox: DOMWrapper<HTMLDivElement>;
    let bceidRadioBox: DOMWrapper<HTMLDivElement>;

    beforeEach(async () => {
        wrapper = mount(UserDomainSelect);

        idirRadioBox = wrapper.find('#idir-test');
        bceidRadioBox = wrapper.find('#bceid-test');
        idirInput = wrapper.find('#idir-test-input');
        bceidInput = wrapper.find('#bceid-test-input');

    });

    it('Should check the checkbox when btn is clicked', async () => {
        await bceidInput.trigger('click');
        expect(idirRadioBox.classes('p-radiobutton-checked')).toBe(true);

        await bceidInput.trigger('click');
        expect(idirRadioBox.classes('p-radiobutton-checked')).toBe(true);

    });

    it('Should call and emit the correct value', async () => {
        await bceidRadioBox.trigger('click');

        emitChange = wrapper.emitted('change');

        //expect emit has been called
        expect(wrapper.emitted()).toHaveProperty('change');

        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(emitChange![0][0]).toEqual(UserType.B);

        await idirRadioBox.trigger('click');

        expect(emitChange![1][0]).toEqual(UserType.I);
    });

    it('Should receive the correct prop', async () => {
        expect(wrapper.props()).toEqual({ domain: UserType.I });

        await wrapper.setProps({ domain: UserType.B });

        expect(wrapper.props()).toEqual({ domain: UserType.B });
    });

    it('Should check the correct radioBtn based on the props', async () => {

        // start with IDIR checked
        expect(idirRadioBox.classes('p-radiobutton-checked')).toBe(true);

        await wrapper.setProps({ domain: UserType.B });
        expect(bceidRadioBox.classes('p-radiobutton-checked')).toBe(true);

        await wrapper.setProps({ domain: UserType.I });
        expect(idirRadioBox.classes('p-radiobutton-checked')).toBe(true);
    });
});
