
<!-- This is a boolean checkbox (true/false) -->

<script setup lang="ts">
import Checkbox from 'primevue/checkbox';

// value to bind parent model.
const model = defineModel()

// configurable options and defaults for props
interface CheckboxProps {
    id?: string;
    label?: string;
    lfontSize?: string;
    lfontWeight?: string;
}
const props = withDefaults(defineProps<CheckboxProps>(), {
    id: "checkbox",
    lfontSize: "0.875rem",
    lfontWeight: "600"
})

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

<style lang="scss">
    @import '@/assets/styles/base.scss';
    .fam-checkbox {
        .p-checkbox {
            margin-right: 0.5rem;
            width: 1.2rem;
            height: 1.2rem;
        }
        label {
            font-size: v-bind('props.lfontSize');
            font-weight: v-bind('props.lfontWeight');
            color: $light-text-secondary;
            margin-bottom: 0;
        }
    }
</style>