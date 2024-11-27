<script setup lang="ts">
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import {
    isAbstractRoleSelected,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import RadioButton from "primevue/radiobutton";
import { ErrorMessage, Field } from "vee-validate";
import { inject, type Ref } from "vue";
import ForestClientSection from "./ForestClientSection.vue";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const props = withDefaults(
    defineProps<{
        appId: number;
        roleOptions: FamRoleDto[];
        label?: string;
        fieldId?: string;
    }>(),
    {
        label: "Assign a role to the user",
        fieldId: "role",
    }
);

const emit = defineEmits(["change", "clearForestClients"]);
</script>

<template>
    <div class="role-select-table-container">
        <label :for="props.fieldId">{{ props.label }}</label>
        <ErrorMessage
            class="table-error invalid-feedback"
            :name="props.fieldId"
        />
        <!-- Field validation with v-model bound to computedRole -->
        <Field
            :name="props.fieldId"
            aria-label="Role Select"
            v-model="formData.forestClients"
        >
            <DataTable :value="roleOptions">
                <template #empty> No role found. </template>
                <Column field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton v-model="formData.role" :value="data" />
                    </template>
                </Column>
                <Column field="roleName" header="Role">
                    <template #body="{ data }">
                        <span>{{ data.display_name }}</span>
                    </template>
                </Column>
                <Column field="roleDescription" header="Description">
                    <template #body="{ data }">
                        <span>{{ data.description }}</span>

                        <ForestClientSection
                            v-if="
                                isAbstractRoleSelected(formData) &&
                                formData.role?.id === data.id
                            "
                            :app-id="props.appId"
                        />
                    </template>
                </Column>
            </DataTable>
        </Field>
    </div>
</template>
<style lang="scss">
.role-select-table-container {
    .p-datatable {
        .p-datatable-thead > tr > th {
            background: var(--layer-accent-01);
        }

        .p-column-header-content .p-column-title {
            padding: 0;
        }

        .p-datatable-tbody > tr > td {
            padding: 1rem;
        }
    }

    .table-error {
        display: block;
    }
}
</style>
