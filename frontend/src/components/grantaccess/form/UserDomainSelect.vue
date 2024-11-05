<script setup lang="ts">
import { computed } from "vue";
import RadioButton from "primevue/radiobutton";
import { UserType } from "fam-app-acsctl-api";
import { IdpProvider } from "@/enum/IdpEnum";

const props = withDefaults(
    defineProps<{
        domain: UserType;
    }>(),
    {
        domain: UserType.B,
    }
);

const emit = defineEmits(["change"]);

const computedDomain = computed({
    get() {
        return props.domain;
    },
    set(newSelectedDomain: string) {
        emit("change", newSelectedDomain);
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
                :value="UserType.I"
            />
            <label class="mx-2" for="idirSelect">{{ IdpProvider.IDIR }}</label>
        </div>
        <div class="px-0">
            <RadioButton
                v-model="computedDomain"
                inputId="businessBceidSelect"
                name="domainRadioOptions"
                :value="UserType.B"
            />
            <label class="mx-2" for="businessBceidSelect">{{
                IdpProvider.BCEIDBUSINESS
            }}</label>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.form-field {
    label {
        margin-bottom: 0px;
    }
}
</style>
