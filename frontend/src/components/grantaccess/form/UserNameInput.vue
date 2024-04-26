<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import InputText from 'primevue/inputtext';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { isLoading } from '@/store/LoadingState';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { IconSize } from '@/enum/IconEnum';
import { IdpProvider } from '@/enum/IdpEnum';
import { UserType, type IdimProxyIdirInfo } from 'fam-app-acsctl-api';

const props = defineProps({
    domain: { type: String, required: true },
    userId: { type: String, default: '' },
    fieldId: { type: String, default: 'userId' },
    helperText: { type: String },
});

const emit = defineEmits(['change', 'setVerifyResult']);

const computedUserId = computed({
    get() {
        return props.userId;
    },
    set(newUserId: string) {
        emit('change', newUserId);
        resetVerifiedUserIdentity();
    },
});

const verifiedUserIdentity = ref<IdimProxyIdirInfo | null>(null);
const verifyUserId = async () => {
    if (props.domain == UserType.B) {
        verifiedUserIdentity.value = (
            await AppActlApiService.idirBceidProxyApi.bceidSearch(
                computedUserId.value
            )
        ).data;
    } else {
        verifiedUserIdentity.value = (
            await AppActlApiService.idirBceidProxyApi.idirSearch(
                computedUserId.value
            )
        ).data;
    }

    verifiedUserIdentity.value = (
        await AppActlApiService.idirBceidProxyApi.idirSearch(
            computedUserId.value
        )
    ).data;

    if (verifiedUserIdentity.value?.found) emit('setVerifyResult', true, verifiedUserIdentity.value.guid);
};
const resetVerifiedUserIdentity = () => {
    verifiedUserIdentity.value = null;
    if (props.domain == UserType.I) emit('setVerifyResult', false);
    else emit('setVerifyResult', true);
};

// whenver user domain change, remove the previous user identity card
watch(
    () => props.domain,
    () => {
        resetVerifiedUserIdentity();
    }
);
</script>

<template>
    <div class="form-field">
        <label for="userIdInput">Username</label>
        <Field
            :name="props.fieldId"
            :validateOnChange="true"
            v-model="computedUserId"
            v-slot="{ errorMessage, field }"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="userIdInput"
                        :placeholder="
                            props.domain === UserType.I
                                ? `Type user\'s ${IdpProvider.IDIR}`
                                : `Type user\'s ${IdpProvider.BCEIDBUSINESS}`
                        "
                        :validateOnChange="true"
                        class="w-100 custom-height"
                        type="text"
                        maxlength="20"
                        v-bind="field"
                        :class="{ 'is-invalid': errorMessage }"
                    />
                    <small
                        id="userIdInput-helper"
                        class="helper-text"
                        v-if="helperText && !errorMessage"
                        >{{ helperText }}</small
                    >
                    <ErrorMessage
                        class="invalid-feedback"
                        :name="props.fieldId"
                        style="display: inline"
                    />
                </div>

                <Button
                    v-if="props.domain === UserType.I"
                    class="w-100 custom-height"
                    :aria-label="`Verify user ${IdpProvider.IDIR}`"
                    name="verifyIdir"
                    label="Verify"
                    @click="verifyUserId()"
                    :disabled="
                        isLoading() ||
                        !computedUserId ||
                        errorMessage !== undefined
                    "
                >
                    <Icon icon="search--locate" :size="IconSize.small" />
                </Button>
                <Button
                    v-else
                    class="w-100 custom-height"
                    :aria-label="`Verify user ${IdpProvider.BCEIDBUSINESS}`"
                    name="verifyBusinessBceid"
                    label="Verify"
                    @click="verifyUserId()"
                    :disabled="
                        isLoading() ||
                        !computedUserId ||
                        errorMessage !== undefined
                    "
                >
                    <Icon icon="search--locate" :size="IconSize.small" />
                </Button>
            </div>
        </Field>

        <div
            v-if="verifiedUserIdentity"
            id="UserIdentityCard"
            class="col-md-5 px-0"
        >
            <UserIdentityCard
                :userIdentity="verifiedUserIdentity"
            ></UserIdentityCard>
        </div>
    </div>
</template>
<style lang="scss" scoped></style>
