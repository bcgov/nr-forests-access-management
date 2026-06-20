<!-- This is a boolean checkbox (true/false) -->

<script setup lang="ts">
import Checkbox from "primevue/checkbox";

// value to bind parent model.
const model = defineModel();

// configurable options and defaults for props
interface CheckboxProps {
    id?: string;
    label?: string;
}
const props = withDefaults(defineProps<CheckboxProps>(), {
    id: "checkbox",
});
</script>

<template>
    <div class="d-flex align-items-center fam-checkbox">
        <Checkbox v-model="model" :inputId="$props.id" binary />
        <div>
            <label v-if="label" for="checkbox" inputId="checkbox-label">
                {{ props.label }}
            </label>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.fam-checkbox {
    :deep(.p-checkbox-box) {
        border-radius: 0;
        height: 1.3rem;
        width: 1.25rem;
    }

    label {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0;
        margin-left: 0.25rem;
        cursor: pointer;
    }
}


</style>
