<template>
    <!-- <b-dropdown v-model="show" class="m-md-2">
        <b-dropdown-header id="dropdown-header-label">
            Dropdown header
        </b-dropdown-header>
        <b-dropdown-item v-for="option in options" :value="option">{{
            option
        }}</b-dropdown-item>
    </b-dropdown> -->
    <b-form-select v-model="selected" :options="options"></b-form-select>

    <validation-provider
        name="Select"
        :rules="{ required: true }"
        v-slot="validationContext"
    >
        <b-form-group
            id="example-input-group-2"
            label="Food"
            label-for="example-input-2"
        >
            <b-form-select
                id="example-input-2"
                name="example-input-2"
                v-model="selected"
                :options="options"
                :state="getValidationState(validationContext)"
                aria-describedby="input-2-live-feedback"
            ></b-form-select>

            <b-form-invalid-feedback id="input-2-live-feedback">{{
                validationContext.errors[0]
            }}</b-form-invalid-feedback>
        </b-form-group>
    </validation-provider>
</template>

<script setup lang="ts">
import { ref, type PropType } from 'vue';

const selected = ref('');
const props = defineProps({
    options: {
        type: Array as PropType<String[]>,
        required: true,
        default: [],
    },
});

function getValidationState({
    dirty,
    validated,
    valid = null,
}): boolean | null {
    return dirty || validated ? valid : null;
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
