<script setup lang="ts">
import { computed, ref } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
// TODO Replace Radio with checkbox once multiple select is implemented
// import Checkbox from 'primevue/checkbox';
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

const selectedRoleId = ref();

const roleIdChanged = () => {
    computedRoleId.value = selectedRoleId.value;
    emit('resetVerifiedForestClients');
};
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
            <div class="data-table-container">
                <div class="role-select-data-table">
                    <DataTable :value="roleOptions">
                        <template #empty> No role found. </template>
                        <template #loading
                            ><ProgressSpinner aria-label="Loading" />
                        </template>
                        <Column field="roleSelect">
                            <template #body="{ data }">
                                <RadioButton
                                    v-model="selectedRoleId"
                                    :value="data.id"
                                    @update:modelValue="handleChange"
                                    @change="roleIdChanged"
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
                            </template></Column
                        >
                    </DataTable>
                </div>
            </div>
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
</style>
