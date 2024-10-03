<script setup lang="ts">
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import { IconSize } from '@/enum/IconEnum';
import { IdpProvider } from '@/enum/IdpEnum';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { selectedApplicationId } from '@/store/ApplicationState';
import FamLoginUserState from '@/store/FamLoginUserState';
import { isLoading } from '@/store/LoadingState';
import type { IdimProxyBceidInfoSchema, IdimProxyIdirInfoSchema } from 'fam-app-acsctl-api';
import { UserType } from 'fam-app-acsctl-api';
import InputText from 'primevue/inputtext';
import { ErrorMessage, Field } from 'vee-validate';
import { computed, ref, watch } from 'vue';

const props = defineProps({
    domain: { type: String, required: true },
    userId: { type: String, default: '' },
    fieldId: { type: String, default: 'userId' },
    helperText: { type: String },
});

const PERMISSION_REQUIRED_FOR_OPERATION = 'permission_required_for_operation';

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

const errorMsg = ref('');

const verifiedUserIdentity = ref<IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null>(
    null
);

/**
 * Checks if the provided user ID matches the currently logged-in user's ID.
 */
 const isCurrentUser = (): boolean => {
    const userId = computedUserId.value?.toLowerCase();
    const loggedInUserId = FamLoginUserState.state.value.famLoginUser?.username?.toLowerCase();

    return userId === loggedInUserId;
};

const verifyUserId = async () => {
    if (!computedUserId.value) {
        return;
    }
    // Guard to forbid users to look up themselves
    if (isCurrentUser()) {
        verifiedUserIdentity.value = {
            found: false,
            userId: computedUserId.value
        }
        errorMsg.value = 'You cannot grant permissions to yourself.';
        return;
    }

    try {
        if (props.domain == UserType.B) {
            verifiedUserIdentity.value = (
                await AppActlApiService.idirBceidProxyApi.bceidSearch(
                    computedUserId.value,
                    selectedApplicationId.value!,
                )
            ).data;
        } else {
            verifiedUserIdentity.value = (
                await AppActlApiService.idirBceidProxyApi.idirSearch(
                    computedUserId.value,
                    selectedApplicationId.value!,
                )
            ).data;
        }
    } catch (error: any) {
        verifiedUserIdentity.value = {
            userId: computedUserId.value,
            found: false,
        };
        if (
            error.response.status === 403 &&
            error.response.data.detail.code ===
                PERMISSION_REQUIRED_FOR_OPERATION
        ) {
            errorMsg.value = `${
                error.response.data.detail.description
            }. Org name: ${
                FamLoginUserState.state.value.famLoginUser!.organization
            }`;
        }
    } finally {
        if (verifiedUserIdentity.value?.found) {
            emit('setVerifyResult', true, verifiedUserIdentity.value.guid, verifiedUserIdentity.value.email);
        }
    }
};
const resetVerifiedUserIdentity = () => {
    verifiedUserIdentity.value = null;
    errorMsg.value = '';
    emit('setVerifyResult', false);
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
                        @keydown.enter.prevent="verifyUserId()"
                        @blur="verifyUserId()"
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
                    class="w-100 custom-height"
                    :aria-label="`Verify user ${
                        props.domain === UserType.I
                            ? IdpProvider.IDIR
                            : IdpProvider.BCEIDBUSINESS
                    }`"
                    :name="
                        props.domain === UserType.I
                            ? 'verifyIdir'
                            : 'verifyBusinessBceid'
                    "
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
            class="user-id-card-container col-md-5 px-0"
        >
            <UserIdentityCard
                :userIdentity="verifiedUserIdentity"
                :errorMsg="errorMsg"
            ></UserIdentityCard>
        </div>
    </div>
</template>

<style lang="scss">
.user-id-card-container {
    @import '@/assets/styles/card.scss';
}
</style>
