<script setup lang="ts">
const props = defineProps<{
    labelText: string;
    for?: string;
    id?: string;
    required?: boolean;
    unstyled?: boolean;
}>();
</script>

<template>
    <label
        :class="{
            'fam-label': !props.unstyled,
        }"
        :for="props.for"
        :id="props.id"
    >
        <span class="required-symbol" v-if="props.required">*</span>
        <span class="label-text">{{ props.labelText }}</span>
    </label>
</template>

<style lang="scss">
.fam-label {
    @include type.type-style("label-02");
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    margin-bottom: 0.5rem;

    .required-symbol {
        color: var(--text-error);
    }

    .label-text {
        color: var(--text-primary);
    }
}
</style>
