<script lang="ts" setup>
import Dropdown, { type DropdownChangeEvent } from "primevue/dropdown";
import InputSkeleton from "@/components/Skeletons/InputSkeleton.vue";
import ErrorText from "@/components/UI/ErrorText.vue";
import type { AxiosError } from "axios";

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
}>();
</script>

<template>
    <div
        :class="
            'fam-dropdown-container' + (props.class ? ` ${props.class}` : '')
        "
    >
        <label v-if="props.labelText" :for="props.name">{{ labelText }}</label>
        <InputSkeleton v-if="props.isFetching" />

        <Dropdown
            v-if="!props.isFetching && !props.isError"
            :id="props.id ?? `${props.name}-id`"
            :name="props.name"
            @change="props.onChange"
            :options="props.options"
            :optionLabel="props.optionLabel"
            placeholder="Choose an application to manage permissions"
            class="fam-dropdown"
            :model-value="props.value"
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
