<script setup lang="ts">
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import Button from "@/components/common/Button.vue";
import UserIdentityCard from "@/components/grantaccess/UserIdentityCard.vue";
import useAuth from "@/composables/useAuth";
import { IconSize } from "@/enum/IconEnum";
import { IdpProvider } from "@/enum/IdpEnum";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { useMutation } from "@tanstack/vue-query";
import type {
    IdimProxyBceidInfoSchema,
    IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api";
import { UserType } from "fam-app-acsctl-api";
import InputText from "primevue/inputtext";
import { ErrorMessage, Field } from "vee-validate";
import { computed, ref, watch } from "vue";

const auth = useAuth();

const props = withDefaults(
    defineProps<{
        domain: UserType;
        userId: string;
        appId: number;
        fieldId?: string;
        helperText?: string;
    }>(),
    {
        fieldId: "userId",
    }
);

const PERMISSION_REQUIRED_FOR_OPERATION = "permission_required_for_operation";

const emit = defineEmits(["change", "setVerifyResult"]);

const computedUserId = computed({
    get() {
        return props.userId;
    },
    set(newUserId: string) {
        emit("change", newUserId);
        resetsearchResult();
    },
});

const errorMsg = ref("");

const searchResult = ref<
    IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null
>(null);

/**
 * Checks if the provided user ID matches the currently logged-in user's ID.
 */
const isCurrentUser = (): boolean => {
    const userId = computedUserId.value?.toLowerCase();
    const loggedInUserId = auth.authState.famLoginUser?.username?.toLowerCase();

    return userId === loggedInUserId;
};

const handleMutationError = (error: any) => {
    searchResult.value = {
        userId: computedUserId.value,
        found: false,
    };

    // Check if error and response properties exist
    if (error.response && error.response.status === 403) {
        const detail = error.response.data?.detail;
        if (detail?.code === PERMISSION_REQUIRED_FOR_OPERATION) {
            errorMsg.value = `${detail.description}. Org name: ${
                auth.authState.famLoginUser?.organization ??
                "Unknown organization"
            }`;
        } else {
            errorMsg.value = "An unknown error occurred.";
        }
    } else {
        errorMsg.value =
            "Unable to verify the user due to a network or server error.";
    }
};

const verifyIdirMutation = useMutation({
    mutationFn: () =>
        AppActlApiService.idirBceidProxyApi
            .idirSearch(computedUserId.value, props.appId)
            .then((res) => res.data),
    onSuccess: (data) => {
        searchResult.value = data;
        emit("setVerifyResult", data.found, data.guid ?? "", data.email ?? "");
    },
    onError: (error) => handleMutationError(error),
});

const verifyBceidMutation = useMutation({
    mutationFn: () =>
        AppActlApiService.idirBceidProxyApi
            .bceidSearch(computedUserId.value, props.appId)
            .then((res) => res.data),
    onSuccess: (data) => {
        searchResult.value = data;
        emit("setVerifyResult", data.found, data.guid ?? "", data.email ?? "");
    },
    onError: (error) => handleMutationError(error),
});

const handleVerify = (userType: UserType) => {
    if (
        verifyBceidMutation.isPending.value ||
        verifyIdirMutation.isPending.value ||
        !computedUserId.value
    ) {
        return;
    }
    if (isCurrentUser()) {
        searchResult.value = {
            found: false,
            userId: computedUserId.value,
        };
        errorMsg.value = "You cannot grant permissions to yourself.";
        return;
    }
    if (userType === "I" && computedUserId.value.length) {
        verifyIdirMutation.mutate();
    }
    if (userType === "B" && computedUserId.value.length) {
        verifyBceidMutation.mutate();
    }
};

const resetsearchResult = () => {
    searchResult.value = null;
    errorMsg.value = "";
    emit("setVerifyResult", false);
};

// whenver user domain change, remove the previous user identity card
watch(
    () => props.domain,
    () => {
        resetsearchResult();
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
                        @keydown.enter.prevent="handleVerify(props.domain)"
                        @blur="handleVerify(props.domain)"
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
                    outlined
                    :icon="SearchLocateIcon"
                    @click="handleVerify(props.domain)"
                    :is-loading="
                        verifyBceidMutation.isPending.value ||
                        verifyIdirMutation.isPending.value
                    "
                >
                    <Icon icon="search--locate" :size="IconSize.small" />
                </Button>
            </div>
        </Field>

        <UserIdentityCard
            v-if="searchResult"
            :userIdentity="searchResult"
            :errorMsg="errorMsg"
        />
    </div>
</template>

<style lang="scss"></style>
