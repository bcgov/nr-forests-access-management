<script setup lang="ts">
import Dropdown from 'primevue/dropdown';
import type { FamApplication } from 'fam-app-acsctl-api';

const props = defineProps({
    label: { type: String, required: false, default: 'Select application' },
    options: {
        type: Array<FamApplication>,
        default: [],
        required: true,
    },
    placeholder: {
        type: String,
        required: false,
        default: 'Choose an application',
    },
});

const modelValue = defineModel<FamApplication>();
</script>

<template>
    <label>{{ label }}</label>
    <Dropdown
        v-model="modelValue"
        :options="props.options"
        optionLabel="application_description"
        :placeholder="props.placeholder"
        class="application-dropdown"
    />
</template>
<style scoped lang="scss">
.application-dropdown {
    max-width: calc(100vw - 3rem);
    height: 3rem;
    padding: 0;

    &:deep(.p-dropdown-label) {
        padding: 0.8375rem 1rem;
    }
}
@media (min-width: 495px) {
    .application-dropdown {
        max-width: 29rem;
    }
}
@media (min-width: 1024px) {
    .application-dropdown {
        max-width: 38rem;
    }
}
</style>
