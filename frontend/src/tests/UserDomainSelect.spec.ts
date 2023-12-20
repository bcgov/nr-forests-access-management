import { it, describe, beforeEach, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import type { DOMWrapper } from '@vue/test-utils/dist/domWrapper';
import { UserType } from 'fam-app-acsctl-api';
import UserDomainSelect from '@/components/grantaccess/form/UserDomainSelect.vue';

describe('UserDomainSelect', () => {
    let wrapper: VueWrapper;
    let idirSelectRadioBtn: DOMWrapper<HTMLInputElement>
    let becidSelectRadioBtn: DOMWrapper<HTMLInputElement>

    beforeEach(async () => {
        wrapper = mount(UserDomainSelect, {
            props: {
                domain: UserType.I,
            },
        });
        idirSelectRadioBtn = wrapper.find('#idirSelect');
        becidSelectRadioBtn = wrapper.find('#becidSelect');
    });

    it('Should call and emit the correct value', () => {

        becidSelectRadioBtn.trigger('click');

        const emitChange = wrapper.emitted(
            'change'
        );

        //expect emit has been called
        expect(wrapper.emitted()).toHaveProperty('change');

        // test the given parameters when emitChange has been called
        // i.e. emitChange = [ [ 'B' ] ]
        expect(
            emitChange
            ? emitChange[0][0]
            : undefined
        ).toEqual(UserType.B);

        idirSelectRadioBtn.trigger('click');

        expect(
            emitChange
            ? emitChange[1][0]
            : undefined
        ).toEqual(UserType.I);

    });

    it('Should receive the correct prop', () => {
        expect(idirSelectRadioBtn.element.value).toEqual(UserType.I);
    });

})