<template>
    <!-- <b-form-radio-group
        v-model="selectedValue"
        :options="props.options"
        @change="valueChanged"
    ></b-form-radio-group> -->
</template>

<script setup lang="ts">
import { ref, onBeforeMount, type PropType } from 'vue';
const props = defineProps({
    options: {
        type: Array as PropType<String[]>,
        required: true,
        default: [],
    },
    initialValue: {
        type: String,
        required: true,
        default: '',
    },
});
const emit = defineEmits(['change']);
const selectedValue = ref<string>('');
onBeforeMount(() => {
    selectedValue.value = props.initialValue;
});
function valueChanged() {
    emit('change', selectedValue.value);
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
