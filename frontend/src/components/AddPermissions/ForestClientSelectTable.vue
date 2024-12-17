<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Checkbox from "primevue/checkbox";
import RadioButton from "primevue/radiobutton";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { useQuery } from "@tanstack/vue-query";
import { Field, useField } from "vee-validate";
import { computed, inject, watch, type Ref } from "vue";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import type { AppPermissionFormType } from "@/views/AddAppPermission/utils";
import Label from "../UI/Label.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";
import { getForestClientsUnderApp } from "@/utils/AuthUtils";
import type { FamForestClientBase } from "fam-admin-mgmt-api/model";
import ErrorText from "../UI/ErrorText.vue";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const props = defineProps<{
    appId: number;
    fieldId: string;
}>();

const { validate: validateForestClients } = useField(props.fieldId);

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => getForestClientsUnderApp(props.appId, data),
    refetchOnMount: true,
});

const availableForestClients = computed<FamForestClientBase[]>(() => {
    const data = adminUserAccessQuery.data.value;
    return data ?? [];
});

watch(
    availableForestClients,
    () => {
        if (availableForestClients.value.length === 1) {
            formData.value.forestClients = availableForestClients.value;
        }
    },
    { immediate: true }
);

const isForestClientSelected = (client: FamForestClientBase) =>
    formData.value.forestClients.some(
        (selectedClient) =>
            selectedClient.forest_client_number === client.forest_client_number
    );

const toggleForestClient = (client: FamForestClientBase) => {
    const index = formData.value.forestClients.findIndex(
        (selectedClient) =>
            selectedClient.forest_client_number === client.forest_client_number
    );
    if (index >= 0) {
        // Remove client if already selected
        formData.value.forestClients.splice(index, 1);
    } else {
        // Add client if not selected
        formData.value.forestClients.push(client);
    }
    // Validate again to remove resolved error if there is any
    validateForestClients();
};
</script>

<template>
    <div class="foresnt-client-select-table-container">
        <SubsectionTitle
            title="Restrict access by organizations"
            subtitle="Select one or more organizations for this to access"
        />

        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            v-model="formData.forestClients"
        >
            <Label label-text="Organizations" required />

            <ErrorText
                v-if="errorMessage"
                show-icon
                :error-msg="errorMessage"
            />

            <!-- Table section -->
            <DataTable class="fam-table" :value="availableForestClients">
                <template #empty>No organization available</template>

                <Column v-if="availableForestClients.length === 1" header="">
                    <template #body="{ data }">
                        <RadioButton
                            class="fam-checkbox"
                            :value="data"
                            v-model="formData.forestClients[0]"
                            readonly
                        />
                    </template>
                </Column>

                <Column v-else header="">
                    <template #body="{ data }">
                        <Checkbox
                            class="fam-checkbox"
                            :binary="true"
                            :model-value="isForestClientSelected(data)"
                            @change="toggleForestClient(data)"
                        />
                    </template>
                </Column>

                <Column header="Name" field="client_name" />

                <Column header="Client number" field="forest_client_number" />
            </DataTable>
        </Field>
    </div>
</template>

<style lang="scss">
.foresnt-client-select-table-container {
    .error-text-container {
        padding: 0;
        height: fit-content;
        margin-bottom: 0.5rem;
    }

    .subsection-title-container {
        margin: 1.5rem 0;
    }

    .input-with-verify-button {
        .add-organization-button {
            width: 12rem;
        }
    }

    .fam-table {
        .p-datatable-emptymessage {
            background-color: var(--layer-01);
        }
    }

    .fam-checkbox {
        display: flex;
        flex-direction: row;
        align-items: center;
        .p-checkbox-box {
            width: 1rem;
            height: 1rem;
        }
    }
}
</style>
