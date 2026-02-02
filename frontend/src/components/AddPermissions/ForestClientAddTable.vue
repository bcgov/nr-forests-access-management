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

const props = defineProps<{
    appId: number;
    fieldId: string;
    formValues: AppPermissionFormType;
    setFieldValue: (field: string, value: any) => void;
}>();

const { setErrors: setForestClientsError } = useField(props.fieldId);


const updateForestClientInput = (
    updates: Partial<AppPermissionFormType["forestClientInput"]>
) => {
    props.setFieldValue("forestClientInput", {
        ...props.formValues.forestClientInput,
        ...updates,
    });
};

const setVerificationError = (errorMessage: string) => {
    updateForestClientInput({
        isValid: false,
        errorMsg: errorMessage,
    });
};

const clearVerificationError = () => {
    setForestClientsError("");
    updateForestClientInput({
        isValid: true,
        errorMsg: "",
    });
};

const clientSearchMutation = useMutation({
    mutationKey: [
        "forest_clients",
        "search",
        {
            client_number: props.formValues.forestClientInput.value,
            application_id: props.appId,
        },
    ],
    mutationFn: (clientNumber: string) => {
        updateForestClientInput({
            isVerifying: true,
        });
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
            setVerificationError(
                "This organization can't be added due to its status"
            );
        } else {
            props.setFieldValue("forestClients", [
                ...props.formValues.forestClients,
                data[0],
            ]);
            updateForestClientInput({
                value: "",
            });
        }
    },
    onError: () => {
        setVerificationError(
            "The organization could not be added. Please try again"
        );
    },
    onSettled: () => {
        updateForestClientInput({
            isVerifying: false,
        });
    },
});

const removeForestClientFromList = (clientNumber: string) => {
    props.setFieldValue(
        "forestClients",
        props.formValues.forestClients.filter(
            (client) => client.forest_client_number !== clientNumber
        )
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
    updateForestClientInput({
        value: newValue,
    });
};

const addOrganization = () => {
    clearVerificationError();

    if (!props.formValues.forestClientInput.value) {
        return;
    }

    if (
        props.formValues.forestClientInput.value.length <
        FOREST_CLIENT_INPUT_MAX_LENGTH
    ) {
        setVerificationError(
            `Client number must be ${FOREST_CLIENT_INPUT_MAX_LENGTH} digits long`
        );
        return;
    }
    // Check duplication
    const duplicate = props.formValues.forestClients.find(
        (client) =>
            client.forest_client_number ===
            props.formValues.forestClientInput.value
    );

    if (duplicate) {
        setVerificationError("Client number has already been added");
        return;
    }

    clientSearchMutation.mutate(props.formValues.forestClientInput.value);
};

onUnmounted(() => {
    clientSearchMutation.reset();
});
</script>

<template>
    <div class="foresnt-client-add-table-container">
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
            :model-value="props.formValues.forestClients"
            @update:model-value="(value) => props.setFieldValue('forestClients', value)"
        >
            <!-- Input section -->
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        :id="props.formValues.forestClientInput.id"
                        class="w-100 custom-height"
                        :value="props.formValues.forestClientInput.value"
                        @input="enforceNumber"
                        @keydown.enter.prevent="addOrganization()"
                        :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH"
                        :class="{
                            'is-invalid': errorMessage || !props.formValues.forestClientInput.isValid,
                        }"
                        :disabled="props.formValues.forestClientInput.isVerifying"
                    />
                    <HelperText
                        :text="
                            errorMessage ||
                            props.formValues.forestClientInput.errorMsg ||
                            'Enter the 8-digit client number'
                        "
                        :is-error="
                            !!(
                                errorMessage ||
                                !props.formValues.forestClientInput.isValid
                            )
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
                    :is-loading="props.formValues.forestClientInput.isVerifying"
                />
            </div>
        </Field>

        <!-- Table section -->
        <DataTable class="fam-table" :value="props.formValues.forestClients">
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
.foresnt-client-add-table-container {
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

        .p-datatable-emptymessage {
            background-color: var(--layer-01);
        }
    }
}
</style>
