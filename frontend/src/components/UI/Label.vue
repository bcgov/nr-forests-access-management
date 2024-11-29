<script setup lang="ts">
const props = defineProps<{
    labelText: string;
    for?: string;
    id?: string;
    required?: boolean;
}>();
</script>

<template>
    <label class="fam-input-label" :for="props.for" :id="props.id">
        <span class="required-symbol" v-if="props.required">*</span>
        <span class="label-text">&nbsp;{{ props.labelText }}</span>
    </label>
</template>

<style lang="scss">
.fam-input-label {
    @include type.type-style("label-02");
    display: flex;
    flex-direction: row;

    .required-symbol {
        color: var(--text-error);
    }

    .label-text {
        color: var(--text-primary);
    }
}
</style>
