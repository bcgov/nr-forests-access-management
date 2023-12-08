<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import * as yup from 'yup';
import InputText from 'primevue/inputtext';
import ApiServiceFactory from '@/services/ApiServiceFactory';
import { requireInjection } from '@/services/utils';
import LoadingState from '@/store/LoadingState';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { IconSize } from '@/enum/IconEnum';
import { UserType, type IdimProxyIdirInfo } from 'fam-app-acsctl-api';

const validationRules = yup
    .string()
    .required('User ID is required')
    .min(2, 'User ID must be at least 2 characters')
    .nullable();

const props = defineProps({
    domain: { type: String, required: true },
    userId: { type: String, default: '' },
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

const appActlApiService = requireInjection(
    ApiServiceFactory.APP_ACCESS_CONTROL_API_SERVICE_KEY
);
const verifiedUserIdentity = ref<IdimProxyIdirInfo | null>(null);
const verifyUserId = async () => {
    if (props.domain == UserType.B) {
        emit('setVerifyResult', true);
        return;
    }

    verifiedUserIdentity.value = (
        await appActlApiService.idirBceidProxyApi.idirSearch(
            computedUserId.value
        )
    ).data;

    if (verifiedUserIdentity.value?.found) emit('setVerifyResult', true);
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
            name="userId"
            :validateOnChange="true"
            v-model="computedUserId"
            v-slot="{ errorMessage, field }"
            :rules="validationRules"
        >
            <div class="input-with-verify-button">
                <InputText
                    id="userIdInput"
                    :placeholder="
                        props.domain === UserType.I
                            ? 'Type user\'s IDIR'
                            : 'Type user\'s BCeID'
                    "
                    :validateOnChange="true"
                    class="w-100 custom-input verify-input"
                    type="text"
                    maxlength="20"
                    v-bind="field"
                    :class="{ 'is-invalid': errorMessage }"
                />
                <Button
                    v-if="props.domain === UserType.I"
                    class="w-100 verify-button"
                    aria-label="Verify user IDIR"
                    :name="'verifyIdir'"
                    :label="'Verify'"
                    @click="verifyUserId()"
                    :disabled="
                        LoadingState.isLoading.value ||
                        !computedUserId ||
                        errorMessage !== undefined
                    "
                >
                    <Icon icon="search--locate" :size="IconSize.small" />
                </Button>
            </div>
            <small
                id="userIdInput-helper"
                class="helper-text"
                v-if="!errorMessage"
                >Enter and verify the username for this user</small
            >
        </Field>
        <ErrorMessage
            class="invalid-feedback"
            name="userId"
            style="display: inline"
        />

        <div class="col-md-5 px-0" v-if="verifiedUserIdentity">
            <UserIdentityCard
                :userIdentity="verifiedUserIdentity"
            ></UserIdentityCard>
        </div>
    </div>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.input-with-verify-button {
    display: flex;
    padding: 0;
}
.verify-input {
    width: 80% !important;
}
.verify-button {
    width: 20% !important;
}
.form-field {
    margin-bottom: 1.5rem;
}
.custom-input {
    max-height: 2.813rem !important;
}
</style>
