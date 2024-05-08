import { it, describe, beforeEach, expect, afterEach } from 'vitest';
import { DOMWrapper, mount } from '@vue/test-utils';
import type { VueWrapper } from '@vue/test-utils/dist/vueWrapper';
import ForestClientCard from '@/components/grantaccess/ForestClientCard.vue';
import {
    STATUS_CODE_ACTIVE,
    STATUS_CODE_INACTIVE,
    STATUS_DESCRIPTION_ACTIVE,
    STATUS_DESCRIPTION_INACTIVE,
    TEST_FOREST_CLIENT_NAME,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER_2,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER_3,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER_2,
    TEST_SUCCESS_FOREST_CLIENT_NUMBER_3,
} from './common/ForestClientData';
import type { FamForestClient } from 'fam-app-acsctl-api';
import { fixJsdomCssErr } from '@/tests/common/fixJsdomCssErr';

fixJsdomCssErr()

const testActiveClient: FamForestClient[] = [
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_SUCCESS_FOREST_CLIENT_NUMBER}`,
        forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER,
        status: {
            status_code: STATUS_CODE_ACTIVE,
            description: STATUS_DESCRIPTION_ACTIVE,
        },
    }
];

const testMultipleActiveClient: FamForestClient[] = [
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_SUCCESS_FOREST_CLIENT_NUMBER}`,
        forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER,
        status: {
            status_code: STATUS_CODE_ACTIVE,
            description: STATUS_DESCRIPTION_ACTIVE,
        },
    },
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_SUCCESS_FOREST_CLIENT_NUMBER_2}`,
        forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER_2,
        status: {
            status_code: STATUS_CODE_ACTIVE,
            description: STATUS_DESCRIPTION_ACTIVE,
        },
    },
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_SUCCESS_FOREST_CLIENT_NUMBER_3}`,
        forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER_3,
        status: {
            status_code: STATUS_CODE_ACTIVE,
            description: STATUS_DESCRIPTION_ACTIVE,
        },
    }
];

const testInactiveClient: FamForestClient[] = [
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_INACTIVE_FOREST_CLIENT_NUMBER}`,
        forest_client_number: TEST_INACTIVE_FOREST_CLIENT_NUMBER,
        status: {
            status_code: STATUS_CODE_INACTIVE,
            description: STATUS_DESCRIPTION_INACTIVE,
        },
    }
];

const testMultipleInactiveClient: FamForestClient[] = [
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_INACTIVE_FOREST_CLIENT_NUMBER}`,
        forest_client_number: TEST_SUCCESS_FOREST_CLIENT_NUMBER,
        status: {
            status_code: STATUS_CODE_INACTIVE,
            description: STATUS_DESCRIPTION_INACTIVE,
        },
    },
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_INACTIVE_FOREST_CLIENT_NUMBER_2}`,
        forest_client_number: TEST_INACTIVE_FOREST_CLIENT_NUMBER_2,
        status: {
            status_code: STATUS_CODE_INACTIVE,
            description: STATUS_DESCRIPTION_INACTIVE,
        },
    },
    {
        client_name: `${TEST_FOREST_CLIENT_NAME}_${TEST_INACTIVE_FOREST_CLIENT_NUMBER_3}`,
        forest_client_number: TEST_INACTIVE_FOREST_CLIENT_NUMBER_3,
        status: {
            status_code: STATUS_CODE_INACTIVE,
            description: STATUS_DESCRIPTION_INACTIVE,
        },
    }
];

describe('ForestClientCard', () => {

    let wrapper: VueWrapper;

    beforeEach(async () => {
        wrapper = mount(ForestClientCard);
    });

    afterEach(() => {
        wrapper.unmount();
    });

    it('should show inactive for forest client card in error case', async () => {
        // Error case
        await wrapper.setProps({ forestClientData: testInactiveClient });
        expect(wrapper.get('#forest-client-status').element.textContent).toBe(STATUS_DESCRIPTION_INACTIVE);
    });

    it('should show active forest client card in successful case', async () => {
        // Success case
        await wrapper.setProps({ forestClientData: testActiveClient });
        expect(wrapper.get('#forest-client-status').element.textContent).toBe(STATUS_DESCRIPTION_ACTIVE);

    });

    it('should show multiple active forest client card in successful case', async () => {
        // Multiple success case
        await wrapper.setProps({ forestClientData: testMultipleActiveClient });
        const clientList = wrapper.findAll('#forest-client-status') as DOMWrapper<Element>[];
        expect(clientList).toHaveLength(3);
        for (let index in clientList) {
            expect(clientList[index].element.textContent).toBe(STATUS_DESCRIPTION_ACTIVE);
        }
    });

    it('should show multiple inactive forest client card in error case', async () => {
        // Multiple success case
        await wrapper.setProps({ forestClientData: testMultipleInactiveClient });
        const clientList = wrapper.findAll('#forest-client-status') as DOMWrapper<Element>[];
        for (let index in clientList) {
            expect(clientList[index].element.textContent).toBe(STATUS_DESCRIPTION_INACTIVE);
        }
    });
});