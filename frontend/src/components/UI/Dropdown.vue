<script lang="ts" setup>
import Dropdown, { type DropdownChangeEvent } from "primevue/dropdown";
import InputSkeleton from "@/components/Skeletons/InputSkeleton.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import Label from "./Label.vue";

const props = defineProps<{
    class: string;
    name: string;
    value: any;
    id?: string;
    optionLabel?: string;
    labelText?: string;
    onChange?: ((event: DropdownChangeEvent) => void) | undefined;
    options?: any[];
    placeholder?: string;
    isFetching?: boolean;
    isError?: boolean;
    errorMsg?: string;
    required?: boolean;
    disabled?: boolean;
}>();
</script>

<template>
    <div
        :class="
            'fam-dropdown-container' + (props.class ? ` ${props.class}` : '')
        "
    >
        <Label
            v-if="props.labelText"
            :for="props.name"
            :label-text="props.labelText"
            :required="props.required"
        />
        <InputSkeleton v-if="props.isFetching" />

        <Dropdown
            v-if="!props.isFetching && !props.isError"
            :id="props.id ?? `${props.name}-id`"
            :name="props.name"
            @change="props.onChange"
            :options="props.options"
            :optionLabel="props.optionLabel"
            :placeholder="props.placeholder"
            class="fam-dropdown"
            :model-value="props.value"
            :disabled="props.disabled"
        />
        <ErrorText v-if="props.isError" :error-msg="errorMsg" show-icon />
    </div>
</template>

<style lang="scss">
.fam-dropdown-container {
    display: flex;
    flex-direction: column;
}
</style>
