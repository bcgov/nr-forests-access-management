<script setup lang="ts">
import { computed } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import Dropdown from 'primevue/dropdown';
import type { FamApplicationRole } from 'fam-app-acsctl-api';
import type { FamRoleDto } from 'fam-admin-mgmt-api/model';

const props = defineProps({
    roleId: { type: Number, default: 0 },
    roleOptions: {
        type: [Array<FamApplicationRole>, Array<FamRoleDto>],
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
            <Dropdown
                :options="roleOptions"
                optionLabel="name"
                optionValue="id"
                :modelValue="field.value"
                placeholder="Choose an option"
                class="w-100 custom-height"
                style="width: 100% !important"
                v-bind="field.value"
                @update:modelValue="handleChange"
                @change="emit('resetVerifiedForestClients')"
                :class="{
                    'is-invalid': errorMessage,
                }"
            />
            <ErrorMessage class="invalid-feedback" :name="props.fieldId" />
        </Field>
    </div>
</template>
<style lang="scss" scoped>
label {
    margin-bottom: 0px;
}
</style>
