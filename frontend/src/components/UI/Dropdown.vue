<script lang="ts" setup>
import Dropdown, { type DropdownChangeEvent } from "primevue/dropdown";
import { useAttrs, type Ref } from "vue";

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
}>();

const emit = defineEmits(["update:modelValue"]);

const handleChange = (e: DropdownChangeEvent) => {
    emit("update:modelValue", e.value);
    if (props.onChange) {
        props.onChange(e);
    }
};
</script>

<template>
    <div
        :class="
            'fam-dropdown-container' + (props.class ? ` ${props.class}` : '')
        "
    >
        <label v-if="props.labelText" :for="props.name">{{ labelText }}</label>
        <Dropdown
            v-if="!props.isFetching"
            :id="props.id ?? `${props.name}-id`"
            :name="props.name"
            @change="handleChange"
            :options="props.options"
            :optionLabel="props.optionLabel"
            placeholder="Choose an application to manage permissions"
            class="fam-dropdown"
            :model-value="props.value"
        />
    </div>
</template>

<style lang="scss">
.fam-dropdown-container {
    display: flex;
    flex-direction: column;
}
</style>
