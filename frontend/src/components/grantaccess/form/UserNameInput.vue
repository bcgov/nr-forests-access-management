<script setup lang="ts">
import { computed, ref } from 'vue';
import { ErrorMessage, Field } from 'vee-validate';
import * as yup from 'yup';
import InputText from 'primevue/inputtext';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { IconSize } from '@/enum/IconEnum';
import type { IdimProxyIdirInfo } from 'fam-app-acsctl-api';

const validationRules = yup
    .string()
    .required('User ID is required')
    .min(2, 'User ID must be at least 2 characters')
    .nullable();

const props = defineProps({
    domain: {
        type: String,
        required: true,
    },
    userId: String,
});

const emit = defineEmits(['change']);
const computedUserId = computed({
    get() {
        return props.userId;
    },
    set(newUserId: string) {
        emit('change', newUserId);
    },
});

const apiServiceFactory = new ApiServiceFactory();
const idirBceidProxyApi = apiServiceFactory.getIdirBceidProxyApi();
const verifiedUserIdentity = ref<IdimProxyIdirInfo | null>(null);
const verifyUserId = async () => {
    if (props.domain == 'B') return;

    verifiedUserIdentity.value = (
        await idirBceidProxyApi.idirSearch(computedUserId.value)
    ).data;
};
</script>

<template>
    <div class="form-field">
        <label for="userIdInput">Username</label>
        <div class="input-with-verify-button">
            <div class="verify-input">
                <Field
                    name="userId"
                    :validateOnChange="true"
                    v-model="computedUserId"
                    v-slot="{ errorMessage, field }"
                    :rules="validationRules"
                >
                    <InputText
                        id="userIdInput"
                        :placeholder="
                            props.domain === 'I'
                                ? 'Type user\'s IDIR'
                                : 'Type user\'s BCeID'
                        "
                        :validateOnChange="true"
                        class="w-100 custom-input"
                        type="text"
                        maxlength="20"
                        v-bind="field"
                        :class="{ 'is-invalid': errorMessage }"
                    />
                    <small
                        id="userIdInput-helper"
                        class="helper-text"
                        v-if="!errorMessage"
                        >Enter and verify the username for this user</small
                    >
                </Field>
                <ErrorMessage class="invalid-feedback" name="userId" />
            </div>
            <div v-if="props.domain === 'I'">
                <Button
                    class="w-100 verify-button"
                    aria-label="Verify user IDIR"
                    :name="'verifyIdir'"
                    :label="'Verify'"
                    @click="verifyUserId()"
                    :disabled="false"
                >
                    <Icon icon="search--locate" :size="IconSize.small" />
                </Button>
            </div>
        </div>

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
    width: 80%;
}
.verify-button {
    width: 20%;
}
.form-field {
    margin-bottom: 1.5rem;
}
.custom-input {
    max-height: 2.813rem !important;
}
</style>
