<script setup lang="ts">
import { ref, watch } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import InputText from 'primevue/inputtext';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { isLoading } from '@/store/LoadingState';
import { FOREST_CLIENT_INPUT_MAX_LENGTH } from '@/store/Constants';
import ForestClientCard from '@/components/grantaccess/ForestClientCard.vue';
import { IconSize } from '@/enum/IconEnum';
import {
    FamForestClientStatusType,
    type FamForestClient,
} from 'fam-app-acsctl-api';

const props = defineProps({
    userId: { type: String, required: true },
    roleId: Number,
    fieldId: { type: String, default: 'forestClientNumbers' }, // field id used in the form validation
});

const emit = defineEmits([
    'setVerifiedForestClients',
    'removeVerifiedForestClients',
    'resetVerifiedForestClients',
]);

const forestClientNumbersInput = ref('');
const forestClientData = ref<FamForestClient[]>([]);
const forestClientNumberVerifyErrors = ref([] as Array<string>);

const verifyForestClientNumber = async (forestClientNumbers: string) => {
    forestClientNumberVerifyErrors.value = [];

    // split by commas and spaces
    let forestNumbers = forestClientNumbers.split(',').map((num) => num.trim());

    for (const forestClientNumber of forestNumbers) {
        if (isForestClientNumberAdded(forestClientNumber)) {
            forestClientNumberVerifyErrors.value.push(
                `Client Number ${forestClientNumber} has already been added.`
            );

            continue;
        }
        await AppActlApiService.forestClientsApi
            .search(forestClientNumber)
            .then((result) => {
                if (!result.data[0]) {
                    forestClientNumberVerifyErrors.value.push(
                        `Client Number ${forestClientNumber} is invalid and cannot be added.`
                    );
                    return;
                }
                if (
                    result.data[0].status?.status_code !==
                    FamForestClientStatusType.A
                ) {
                    forestClientNumberVerifyErrors.value.push(
                        `Client Number ${forestClientNumber} is inactive and cannot be added.`
                    );
                    return;
                }

                forestClientData.value.push(result.data[0]);
                emit(
                    'setVerifiedForestClients',
                    result.data[0].forest_client_number
                );
                forestNumbers = forestNumbers.filter(
                    (number) => number !== forestClientNumber
                ); //Remove successfully added numbers so the user can edit in the input only errored ones
            })
            .catch(() => {
                forestClientNumberVerifyErrors.value.push(
                    `An error has occurred. Client Number ${forestClientNumber} could not be added.`
                );
            });
    }

    //The input is updated with only the numbers that have errored out. The array is converted to a string values comma separated
    forestClientNumbersInput.value = forestNumbers.toString();
};

const isForestClientNumberAdded = (forestClientNumber: string) => {
    return forestClientData.value.find(
        (item) => forestClientNumber === item.forest_client_number
    );
};

const removeForestClientFromList = (index: number) => {
    // remove the verified forest client from card
    forestClientData.value.splice(index, 1);
    // remove the verified forest client number from form data
    emit('removeVerifiedForestClients', index);
};

const cleanupForestClientNumberInput = () => {
    forestClientNumbersInput.value = '';
    forestClientNumberVerifyErrors.value = [];
};

const cleanupForestClientSection = () => {
    // cleanup the forest client number input field and verification errors
    cleanupForestClientNumberInput();
    // remove the forest client card data
    forestClientData.value = [];
    // remove the verified forest client numbers which already added to form data
    emit('resetVerifiedForestClients');
};

// whenever user id or abstract role id changed, cleanup the forest client section
watch(
    () => props.userId,
    () => cleanupForestClientSection()
);
watch(
    () => props.roleId,
    () => cleanupForestClientSection()
);
</script>

<template>
    <div>
        <label for="forestClientInput"
            >Add one or more client numbers (8 digits)
        </label>
        <Field
            :name="props.fieldId"
            v-slot="{ field, errorMessage }"
            v-model="forestClientNumbersInput"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="forestClientInput"
                        placeholder="Enter and verify the client number"
                        v-bind="field"
                        class="w-100 custom-height"
                        @input="cleanupForestClientNumberInput()"
                        @keydown.enter.prevent="
                            field.value &&
                                !errorMessage &&
                                verifyForestClientNumber(
                                    forestClientNumbersInput
                                )
                        "
                        :class="{
                            'is-invalid':
                                errorMessage ||
                                forestClientNumberVerifyErrors.length > 0,
                        }"
                    />
                    <small
                        id="forestClientInput-help"
                        class="helper-text"
                        v-if="
                            !errorMessage &&
                            forestClientNumberVerifyErrors.length === 0
                        "
                        >Add and verify the Client Numbers. Add multiple numbers
                        by separating them with commas</small
                    >
                    <ErrorMessage
                        class="invalid-feedback"
                        :name="props.fieldId"
                        style="display: block"
                    />
                    <small
                        id="forestClientInputValidationError"
                        class="invalid-feedback"
                        v-for="error in forestClientNumberVerifyErrors"
                        style="display: block"
                    >
                        {{ error }}
                    </small>
                </div>
                <Button
                    class="w-100 custom-height"
                    aria-label="Add Client Numbers"
                    name="verifyFC"
                    label="Add Client Numbers"
                    @click="verifyForestClientNumber(forestClientNumbersInput)"
                    v-bind:disabled="
                        forestClientNumbersInput?.length <
                            FOREST_CLIENT_INPUT_MAX_LENGTH ||
                        !!errorMessage ||
                        isLoading()
                    "
                >
                    <Icon icon="add" :size="IconSize.small" />
                </Button>
            </div>
        </Field>
    </div>

    <ForestClientCard
        v-if="forestClientData.length > 0"
        class="px-0"
        :forestClientData="forestClientData"
        @remove-item="removeForestClientFromList"
    />
</template>
