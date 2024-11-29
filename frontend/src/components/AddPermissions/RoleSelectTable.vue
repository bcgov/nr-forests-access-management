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
import { inject, watch, type Ref } from "vue";
import ForestClientSection from "./ForestClientSection.vue";
import Label from "../UI/Label.vue";

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
        label: "Role",
        fieldId: "role",
    }
);
</script>

<template>
    <div class="role-select-table-container">
        <Label :for="props.fieldId" :label-text="props.label" required />

        <ErrorMessage
            class="table-error invalid-feedback"
            :name="props.fieldId"
        />
        <!-- Field validation with v-model bound to computedRole -->
        <Field
            :name="props.fieldId"
            aria-label="Role Select"
            v-model="formData.role"
        >
            <DataTable :value="roleOptions" class="fam-table">
                <template #empty> No role found. </template>
                <Column field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton :value="data" v-model="formData.role" />
                    </template>
                </Column>
                <Column class="role-name-col" field="roleName" header="Role">
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
                            field-id="forestClients"
                        />
                    </template>
                </Column>
            </DataTable>
        </Field>
    </div>
</template>
<style lang="scss">
.role-select-table-container {
    margin-top: 2.5rem;

    td.role-name-col {
        display: flex;
        flex-direction: row;
        align-items: start;
    }

    .p-datatable {
        .p-datatable-tbody > tr:hover {
            background-color: colors.$white;
        }
    }

    .table-error {
        display: block;
    }
}
</style>
