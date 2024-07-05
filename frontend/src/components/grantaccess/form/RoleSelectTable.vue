<script setup lang="ts">
import { computed } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import RadioButton from 'primevue/radiobutton';
import ProgressSpinner from 'primevue/progressspinner';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';

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
    set(newRoleId: Number) {
        emit('change', newRoleId);
    },
});
</script>

<template>
    <div class="form-field">
        <label>{{ props.label }}</label>
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
                <Column class="role-section-table-column" field="roleSelect">
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
                    class="role-section-table-column"
                    field="roleName"
                    header="Role"
                    ><template #body="{ data }">
                        <span>
                            {{ data.name }}
                        </span>
                    </template></Column
                >
                <Column
                    class="role-section-table-column"
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

.role-section-table-column {
    padding: 1rem !important;
}
</style>
