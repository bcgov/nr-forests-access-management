<script setup lang="ts">
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import ProgressSpinner from "primevue/progressspinner";
import RadioButton from "primevue/radiobutton";
import { ErrorMessage, Field } from "vee-validate";
import { computed } from "vue";

const props = withDefaults(
    defineProps<{
        role: FamRoleDto | null;
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

const computedRole = computed({
    get() {
        return props.role;
    },
    set(selectedRole: FamRoleDto | null) {
        emit("change", selectedRole);
    },
});
</script>

<template>
    <div class="form-field">
        <label :for="props.fieldId">{{ props.label }}</label>
        <Field
            :name="props.fieldId"
            aria-label="Role Select"
            v-slot="{ errorMessage }"
            v-model="computedRole"
        >
            <DataTable :value="roleOptions">
                <template #empty> No role found. </template>
                <template #loading>
                    <ProgressSpinner aria-label="Loading" />
                </template>
                <Column field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton
                            v-model="computedRole"
                            :value="data"
                            @change="emit('clearForestClients')"
                            :class="{
                                'is-invalid': errorMessage,
                            }"
                        ></RadioButton>
                    </template>
                </Column>
                <Column field="roleName" header="Role"
                    ><template #body="{ data }">
                        <span>
                            {{ data.name }}
                        </span>
                    </template></Column
                >
                <Column field="roleDescription" header="Description">
                    <template #body="{ data }">
                        <span>
                            {{ data.description }}
                        </span>
                    </template>
                </Column>
            </DataTable>

            <ErrorMessage class="invalid-feedback" :name="props.fieldId" />
        </Field>
    </div>
</template>
<style lang="scss">
.p-datatable {
    .p-column-header-content .p-column-title {
        padding: 0;
    }

    .p-datatable-tbody > tr > td {
        padding: 1rem;
    }
}
</style>
