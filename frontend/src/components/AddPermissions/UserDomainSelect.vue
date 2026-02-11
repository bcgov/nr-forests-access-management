<script setup lang="ts">
import { IdpProvider } from "@/enum/IdpEnum";
import { UserType } from "fam-app-acsctl-api";
import RadioButton from "primevue/radiobutton";
import { toRef } from "vue";
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

const emit = defineEmits(["domain-change-request"]);

// Local state for the selected domain, always synced from prop.
// By calling toRef(props, "domain"), it gives a Ref object (localDomain) that always reflects
// the current value of props.domain and updates reactively if the parent changes the prop.
const localDomain = toRef(props, "domain");

// Emit change request, but do not update localDomain until parent confirms
const handleDomainChange = (newDomain: UserType) => {
    emit("domain-change-request", newDomain);
};
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
                    :model-value="localDomain"
                    inputId="idirSelect"
                    name="domainRadioOptions"
                    :value="UserType.I"
                    :disabled="props.isVerifyingUser"
                    @update:model-value="handleDomainChange"
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
                    :model-value="localDomain"
                    inputId="businessBceidSelect"
                    name="domainRadioOptions"
                    :value="UserType.B"
                    :disabled="props.isVerifyingUser"
                    @update:model-value="handleDomainChange"
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
