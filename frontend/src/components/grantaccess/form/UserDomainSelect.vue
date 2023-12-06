<script setup lang="ts">
import { computed } from 'vue';
import RadioButton from 'primevue/radiobutton';

const domainOptions = { IDIR: 'I', BCEID: 'B' };

const props = defineProps({
    domain: {
        type: String,
        default: 'I',
    },
});

const emit = defineEmits(['change']);

const computedDomain = computed({
    get() {
        return props.domain;
    },
    set(newSelectedDomain: string) {
        emit('change', newSelectedDomain);
    },
});
</script>

<template>
    <div class="user-radio-group">
        <label> Select user's domain </label>
        <div class="px-0">
            <RadioButton
                v-model="computedDomain"
                inputId="idirSelect"
                name="domainRadioOptions"
                :value="domainOptions.IDIR"
            />
            <label class="mx-2" for="idirSelect">IDIR</label>
        </div>
        <div class="px-0">
            <RadioButton
                v-model="computedDomain"
                inputId="becidSelect"
                name="domainRadioOptions"
                :value="domainOptions.BCEID"
            />
            <label class="mx-2" for="becidSelect">BCeID</label>
        </div>
    </div>
</template>
<style lang="scss" scoped></style>
