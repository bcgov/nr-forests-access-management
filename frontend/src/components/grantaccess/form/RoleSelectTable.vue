<script setup lang="ts">
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';
import RadioButton from 'primevue/radiobutton';
import { ErrorMessage, Field } from 'vee-validate';
import { computed } from 'vue';

const props = defineProps({
    roleId: { type: Number, default: 0 },
    roleOptions: {
        type: [Array<FamRoleDto>],
        default: [],
    },
    label: { type: String, default: 'Assign a role to the user' },
    fieldId: { type: String, default: 'roleId' },
});

const emit = defineEmits(['change', 'resetVerifiedForestClients']);

const computedRoleId = computed({
    get() {
        return props.roleId;
    },
    set(newRoleId: number) {
        emit('change', newRoleId);
    },
});
</script>

<template>
    <div class="form-field">
        <label :for="props.fieldId">{{ props.label }}</label>
        <Field
            :name="props.fieldId"
            aria-label="Role Select"
            v-slot="{ field, handleChange, errorMessage }"
            v-model="computedRoleId"
        >
            <DataTable :value="roleOptions">
                <template #empty> No role found. </template>
                <template #loading
                    ><ProgressSpinner aria-label="Loading" />
                </template>
                <Column field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton
                            v-model="computedRoleId"
                            :value="data.id"
                            @update:modelValue="handleChange"
                            @change="emit('resetVerifiedForestClients')"
                            :class="{
                                'is-invalid': errorMessage,
                            }"
                        ></RadioButton>
                    </template>
                </Column>
                <Column
                    field="roleName"
                    header="Role"
                    ><template #body="{ data }">
                        <span>
                            {{ data.name }}
                        </span>
                    </template></Column
                >
                <Column
                    field="roleDescription"
                    header="Description"
                >
                    <template #body="{ data }">
                        <span>
                            {{ data.description }}
                        </span>
                    </template></Column
                >
            </DataTable>

            <ErrorMessage class="invalid-feedback" :name="props.fieldId" />
        </Field>
    </div>
</template>
<style lang="scss">
label {
    margin-bottom: 0px;
}

.role-select-data-table .p-column-header-content .p-column-title {
    padding: 0;
}

// Only apply on PrimeVue datatable tbody columns, not on header.
.p-datatable {
    tbody {
        td {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
}

</style>
