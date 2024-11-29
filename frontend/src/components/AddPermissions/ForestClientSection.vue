<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "@/components/UI/Button.vue";
import AddIcon from "@carbon/icons-vue/es/add/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { useMutation } from "@tanstack/vue-query";
import InputText from "primevue/inputtext";
import { Field, useField } from "vee-validate";
import { inject, onUnmounted, ref, type Ref } from "vue";
import { FOREST_CLIENT_INPUT_MAX_LENGTH } from "@/constants/constants";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import type { AppPermissionFormType } from "@/views/AddAppPermission/utils";
import Label from "../UI/Label.vue";
import Chip from "../UI/Chip.vue";
import HelperText from "../UI/HelperText.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";

const INACTIVE_ERROR =
    "This organization can’t be added due to its status. For more information ";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const props = defineProps<{
    appId: number;
    fieldId: string;
    setIsVerifyingClient: (verifying: boolean) => void;
}>();

const { validate } = useField(props.fieldId);

const verificationError = ref<boolean>(false);
const verificationErrorMessage = ref<string>("");

const isVerifying = ref<boolean>(false);
const forestClientNumberInput = ref("");

const setVerificationError = (errorMessage: string) => {
    verificationError.value = true;
    verificationErrorMessage.value = errorMessage;
};

const clearVerificationError = () => {
    verificationError.value = false;
    verificationErrorMessage.value = "";
};

const clientSearchMutation = useMutation({
    mutationKey: [
        "forest_clients",
        "search",
        {
            client_number: forestClientNumberInput.value,
            application_id: props.appId,
        },
    ],
    mutationFn: (clientNumber: string) => {
        isVerifying.value = true;
        props.setIsVerifyingClient(isVerifying.value);
        return AppActlApiService.forestClientsApi
            .search(clientNumber, props.appId)
            .then((res) => res.data);
    },
    onSuccess: (data) => {
        if (!data.length) {
            setVerificationError(
                "No organization found. Check the client number and try again"
            );
        } else if (data[0].status?.status_code !== "A") {
            setVerificationError(INACTIVE_ERROR);
        } else {
            formData.value.forestClients.push(data[0]);
            forestClientNumberInput.value = "";
        }
    },
    onError: () => {
        setVerificationError(
            "The organization could not be added. Please try again"
        );
    },
    onSettled: () => {
        isVerifying.value = false;
        props.setIsVerifyingClient(isVerifying.value);
        validate();
    },
});

const removeForestClientFromList = (clientNumber: string) => {
    formData.value.forestClients.splice(
        formData.value.forestClients.findIndex(
            (client) => client.forest_client_number === clientNumber
        ),
        1
    );
};

const enforceNumber = (event: Event) => {
    const target = event.target as HTMLInputElement;
    let newValue = "";

    for (const char of target.value) {
        if (char >= "0" && char <= "9") {
            newValue += char;
        }
    }

    target.value = newValue;
    forestClientNumberInput.value = newValue;
};

const addOrganization = () => {
    clearVerificationError();

    if (!forestClientNumberInput.value) {
        return;
    }
    // Check duplication
    const duplicate = formData.value.forestClients.find(
        (client) =>
            client.forest_client_number === forestClientNumberInput.value
    );

    if (duplicate) {
        setVerificationError("Client number has already been added");
        return;
    }

    clientSearchMutation.mutate(forestClientNumberInput.value);
};

onUnmounted(() => {
    clientSearchMutation.reset();
});
</script>

<template>
    <div class="foresnt-client-section-container">
        <SubsectionTitle
            title="Restrict access by organizations"
            subtitle="Add one or more organizations for this user to have access to"
        />
        <Label
            for="forestClientInput"
            label-text="Organization's client number"
            required
        />
        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            v-model="formData.forestClients"
        >
            <!-- Input section -->
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="forestClientInput"
                        class="w-100 custom-height"
                        v-model="forestClientNumberInput"
                        :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH"
                        @input="enforceNumber"
                        @keydown.enter.prevent="addOrganization()"
                        :class="{
                            'is-invalid': errorMessage || verificationError,
                        }"
                        @blur="addOrganization()"
                        :disabled="isVerifying"
                    />
                    <HelperText
                        :text="
                            errorMessage ||
                            verificationErrorMessage ||
                            'Enter the 8-digit client number'
                        "
                        :is-error="!!(errorMessage || verificationError)"
                        :link="
                            verificationErrorMessage === INACTIVE_ERROR
                                ? 'https://github.com/bcgov/nr-forest-client/'
                                : undefined
                        "
                        :link-label="
                            verificationErrorMessage === INACTIVE_ERROR
                                ? 'Go to Client Management System'
                                : undefined
                        "
                    />
                </div>
                <Button
                    outlined
                    class="add-organization-button"
                    aria-label="add organizations"
                    name="add organizations"
                    label="Add organization"
                    @click="addOrganization"
                    :icon="AddIcon"
                    :is-loading="isVerifying"
                />
            </div>
        </Field>

        <!-- Table section -->
        <DataTable class="fam-table" :value="formData.forestClients">
            <template #empty>No organization added yet</template>

            <Column header="Client number" field="forest_client_number" />

            <Column header="Name" field="client_name" />

            <Column header="Status">
                <template #body="{ data }">
                    <Chip
                        v-tooltip.top="
                            'Current status of this organization in the Client Management System'
                        "
                        color="green"
                        :label="data.status.description"
                    />
                </template>
            </Column>

            <Column header="Action">
                <template #body="{ data }">
                    <Button
                        icon-only
                        :icon="TrashIcon"
                        @click="
                            removeForestClientFromList(
                                data.forest_client_number
                            )
                        "
                    />
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<style lang="scss">
.foresnt-client-section-container {
    .subsection-title-container {
        margin: 1.5rem 0;
    }

    .input-with-verify-button {
        .add-organization-button {
            width: 12rem;
        }
    }

    .fam-table {
        margin-top: 1.5rem;
    }
}
</style>
