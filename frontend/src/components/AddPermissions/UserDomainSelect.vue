<script setup lang="ts">
import { computed } from "vue";
import RadioButton from "primevue/radiobutton";
import { UserType } from "fam-app-acsctl-api";
import { IdpProvider } from "@/enum/IdpEnum";
import Label from "../UI/Label.vue";

const props = withDefaults(
    defineProps<{
        domain: UserType;
        isVerifyingUser: boolean;
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
    <div class="form-field container">
        <div class="row">
            <div class="col">
                <Label labelText="User's domain" required />
            </div>
        </div>

        <div class="row">
            <div class="col idp-select-col">
                <RadioButton
                    v-model="computedDomain"
                    inputId="idirSelect"
                    name="domainRadioOptions"
                    :value="UserType.I"
                    :disabled="props.isVerifyingUser"
                />
                <Label
                    for="idirSelect"
                    :labelText="IdpProvider.IDIR"
                    unstyled
                />
            </div>
        </div>
        <div class="row">
            <div class="col idp-select-col">
                <RadioButton
                    v-model="computedDomain"
                    inputId="businessBceidSelect"
                    name="domainRadioOptions"
                    :value="UserType.B"
                    :disabled="props.isVerifyingUser"
                />
                <Label
                    for="businessBceidSelect"
                    :labelText="IdpProvider.BCEIDBUSINESS"
                    unstyled
                />
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.form-field {
    display: flex;
    flex-direction: column;
    row-gap: 0.5rem;
    padding: 0;
    margin: 0;

    .idp-select-col {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 0.5rem;

        label {
            @include type.type-style("body-compact-01");
        }
    }
}
</style>
