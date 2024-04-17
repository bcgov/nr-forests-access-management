<script setup lang="ts">
import { computed } from 'vue';
import RadioButton from 'primevue/radiobutton';
import { UserType } from 'fam-app-acsctl-api';
import { IdpProvider } from '@/enum/IdpEnum';

const domainOptions = { IDIR: UserType.I, BCEID: UserType.B };

const props = defineProps({
    domain: { type: String, default: UserType.I },
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
    <div class="form-field">
        <label> Select user's domain </label>
        <div class="px-0">
            <RadioButton
                v-model="computedDomain"
                inputId="idirSelect"
                name="domainRadioOptions"
                :value="domainOptions.IDIR"
            />
            <label class="mx-2" for="idirSelect">{{ IdpProvider.IDIR }}</label>
        </div>
        <div class="px-0">
            <RadioButton
                v-model="computedDomain"
                inputId="businessBceidSelect"
                name="domainRadioOptions"
                :value="domainOptions.BCEID"
            />
            <label class="mx-2" for="businessBceidSelect">{{
                IdpProvider.BCEIDBUSINESS
            }}</label>
        </div>
    </div>
</template>
<style lang="scss" scoped>
label {
    margin-bottom: 0px;
}
</style>
