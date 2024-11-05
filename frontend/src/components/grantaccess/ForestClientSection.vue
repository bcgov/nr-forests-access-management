<script setup lang="ts">
import Button from "@/components/common/Button.vue";
import Icon from "@/components/common/Icon.vue";
import ForestClientCard from "@/components/grantaccess/ForestClientCard.vue";
import Spinner from "@/components/UI/Spinner.vue";
import { IconSize } from "@/enum/IconEnum";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { selectedApplicationId } from "@/store/ApplicationState";
import { FOREST_CLIENT_INPUT_MAX_LENGTH } from "@/store/Constants";
import { useMutation } from "@tanstack/vue-query";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import { type FamForestClientSchema } from "fam-app-acsctl-api";
import InputText from "primevue/inputtext";
import { ErrorMessage, Field } from "vee-validate";
import { computed, ref, watch } from "vue";

const props = withDefaults(
    defineProps<{
        userId: string;
        role: FamRoleDto | null;
        appId: number;
        fieldId?: string;
    }>(),
    {
        fieldId: "forestClientNumbers",
    }
);

const emit = defineEmits(["setVerifiedForestClients"]);

const setVerifiedForestClients = (ids: string[]) =>
    emit("setVerifiedForestClients", ids);

const forestClientNumbersInput = ref("");
const numbersToVerify = ref<string[]>([]);

const forestClientData = ref<FamForestClientSchema[]>([]);
const forestClientNumberVerifyErrors = ref([] as Array<string>);

// const verifyForestClientNumber = async (forestClientNumbers: string) => {
//     forestClientNumberVerifyErrors.value = [];

//     // split by commas and spaces
//     let forestNumbers = forestClientNumbers.split(",").map((num) => num.trim());

//     for (const forestClientNumber of forestNumbers) {
//         if (isForestClientNumberAdded(forestClientNumber)) {
//             forestClientNumberVerifyErrors.value.push(
//                 `Client Number ${forestClientNumber} has already been added.`
//             );

//             continue;
//         }
//         await AppActlApiService.forestClientsApi
//             .search(forestClientNumber, selectedApplicationId.value!)
//             .then((result) => {
//                 if (!result.data[0]) {
//                     forestClientNumberVerifyErrors.value.push(
//                         `Client Number ${forestClientNumber} is invalid and cannot be added.`
//                     );
//                     return;
//                 }
//                 if (
//                     result.data[0].status?.status_code !==
//                     FamForestClientStatusType.A
//                 ) {
//                     forestClientNumberVerifyErrors.value.push(
//                         `Client Number ${forestClientNumber} is inactive and cannot be added.`
//                     );
//                     return;
//                 }

//                 forestClientData.value.push(result.data[0]);
//                 emit(
//                     "setVerifiedForestClients",
//                     result.data[0].forest_client_number
//                 );
//                 forestNumbers = forestNumbers.filter(
//                     (number) => number !== forestClientNumber
//                 ); //Remove successfully added numbers so the user can edit in the input only errored ones
//             })
//             .catch(() => {
//                 forestClientNumberVerifyErrors.value.push(
//                     `An error has occurred. Client Number ${forestClientNumber} could not be added.`
//                 );
//             });
//     }

//     //The input is updated with only the numbers that have errored out. The array is converted to a string values comma separated
//     forestClientNumbersInput.value = forestNumbers.toString();
// };

const cleanupForestClientSection = () => {
    // remove the verified forest client numbers which already added to form data
    setVerifiedForestClients([]);

    forestClientNumberVerifyErrors.value = [];

    // remove the forest client card data
    forestClientData.value = [];
};

const clientSearchMutation = useMutation({
    mutationFn: (clientNumber: string) => {
        return AppActlApiService.forestClientsApi
            .search(clientNumber, props.appId)
            .then((res) => res.data);
    },
    onMutate: (clientNumber) => {
        // Store the client number in context so it’s available in onSuccess and onError
        return { clientNumber };
    },
    onSuccess: (data, _variables, context) => {
        if (data.length) {
            forestClientData.value.push(data[0]);
        } else {
            forestClientNumberVerifyErrors.value.push(
                `An error has occurred. Client Number ${context.clientNumber} could not be added.`
            );
        }
    },
    onError: (_error, _variables, context) => {
        // Access clientNumber from context
        if (context?.clientNumber) {
            forestClientNumberVerifyErrors.value.push(
                `An error has occurred. Client Number ${context.clientNumber} could not be added.`
            );
        }
    },
});

const isVerifying = ref<boolean>(false);

const handleVerifyClients = async () => {
    if (!isVerifying.value) {
        isVerifying.value = true;
        cleanupForestClientSection();
        const verifyPromises = numbersToVerify.value.map((clientNumber) =>
            clientSearchMutation.mutateAsync(clientNumber)
        );
        await Promise.allSettled(verifyPromises);

        isVerifying.value = false;
        setVerifiedForestClients(
            forestClientData.value.map((fc) => fc.forest_client_number)
        );
    }
};

const removeForestClientFromList = (clientNumber: string) => {
    // remove the verified forest client from card
    forestClientData.value = forestClientData.value.filter(
        (client) => client.forest_client_number !== clientNumber
    );

    // remove the verified forest client number from form data
    setVerifiedForestClients(
        forestClientData.value.map((client) => client.forest_client_number)
    );
};

// whenever user id or abstract role changed, cleanup the forest client section
watch(
    () => props.userId,
    () => cleanupForestClientSection()
);
watch(
    () => props.role,
    () => cleanupForestClientSection()
);

const parseAndCleanNumbers = (input: string): string[] => {
    return Array.from(
        new Set(
            input
                .split(",")
                .map((num) => num.trim()) // Remove any surrounding spaces
                .filter((num) => num) // Remove empty strings if there are multiple commas
        )
    );
};

const handleFcInput = () => {
    numbersToVerify.value = parseAndCleanNumbers(
        forestClientNumbersInput.value
    );
    handleVerifyClients();
};
</script>

<template>
    <div>
        <label for="forestClientInput"
            >Add one or more client numbers (8 digits)
        </label>
        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            v-model="forestClientNumbersInput"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="forestClientInput"
                        placeholder="Enter and verify the client number"
                        class="w-100 custom-height"
                        v-model="forestClientNumbersInput"
                        @blur="handleFcInput"
                        @keydown.enter.prevent="
                            forestClientNumbersInput.length &&
                                !errorMessage &&
                                handleFcInput()
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
                    @click="handleVerifyClients"
                    v-bind:disabled="
                        forestClientNumbersInput?.length <
                            FOREST_CLIENT_INPUT_MAX_LENGTH || !!errorMessage
                    "
                >
                    <Spinner v-if="isVerifying" small is-white />
                    <Icon v-else icon="add" :size="IconSize.small" />
                </Button>
            </div>
        </Field>
    </div>

    <!-- <ForestClientCard
        v-if="forestClientData.length > 0"
        class="fores-client-card-container px-0"
        :forestClientData="forestClientData"
        @remove-item="removeForestClientFromList"
    /> -->
</template>

<style lang="scss">
.fores-client-card-container {
    @import "@/assets/styles/card.scss";
}
</style>
