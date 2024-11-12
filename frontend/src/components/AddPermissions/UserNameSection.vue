<script setup lang="ts">
import { ref, watch } from "vue";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import Button from "@/components/UI/Button.vue";
import UserIdentityCard from "@/components/AddPermissions/UserIdentityCard.vue";
import useAuth from "@/composables/useAuth";
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

const auth = useAuth();

const props = withDefaults(
    defineProps<{
        domain: UserType;
        user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null;
        appId: number;
        fieldId?: string;
        helperText?: string;
    }>(),
    {
        fieldId: "user",
    }
);

const PERMISSION_REQUIRED_FOR_OPERATION = "permission_required_for_operation";

const emit = defineEmits(["setVerifyResult"]);

const userIdInput = ref<string>("");

const errorMsg = ref("");

/**
 * Checks if the provided user ID matches the currently logged-in user's ID.
 */
const isCurrentUser = (): boolean => {
    const userId = userIdInput.value?.toLowerCase();
    const loggedInUserId = auth.authState.famLoginUser?.username?.toLowerCase();

    return userId === loggedInUserId;
};

const handleMutationError = (error: any) => {
    emit("setVerifyResult", null);

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
            .idirSearch(userIdInput.value, props.appId)
            .then((res) => res.data),
    onSuccess: (data) => {
        emit("setVerifyResult", data, UserType.I);
    },
    onError: (error) => handleMutationError(error),
});

const verifyBceidMutation = useMutation({
    mutationFn: () =>
        AppActlApiService.idirBceidProxyApi
            .bceidSearch(userIdInput.value, props.appId)
            .then((res) => res.data),
    onSuccess: (data) => {
        emit("setVerifyResult", data, UserType.B);
    },
    onError: (error) => handleMutationError(error),
});

const handleVerify = (userType: UserType) => {
    if (
        verifyBceidMutation.isPending.value ||
        verifyIdirMutation.isPending.value ||
        !userIdInput.value
    ) {
        return;
    }
    if (isCurrentUser()) {
        console.log("hahah");
        emit("setVerifyResult", null);
        errorMsg.value = "You cannot grant permissions to yourself.";
        return;
    }
    errorMsg.value = "";
    if (userType === "I") {
        verifyIdirMutation.mutate();
    }
    if (userType === "B") {
        verifyBceidMutation.mutate();
    }
};

const resetsearchResult = () => {
    errorMsg.value = "";
    emit("setVerifyResult", null);
};

// whenver user domain change, remove the previous user identity card
watch(
    () => props.domain,
    () => {
        userIdInput.value = "";
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
            v-slot="{ errorMessage }"
            v-model="props.user"
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
                        v-model="userIdInput"
                        :class="{ 'is-invalid': errorMessage || errorMsg }"
                        @keydown.enter.prevent="handleVerify(props.domain)"
                        @blur="handleVerify(props.domain)"
                    />
                    <small
                        id="userIdInput-helper"
                        class="helper-text"
                        v-if="helperText && !errorMessage && !errorMsg"
                        >{{ helperText }}</small
                    >
                    <small
                        id="userIdInput-err-msg"
                        class="invalid-feedback"
                        v-if="errorMsg"
                        >{{ errorMsg }}</small
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
                </Button>
            </div>
        </Field>

        <UserIdentityCard
            v-if="user"
            :userIdentity="user"
            :errorMsg="errorMsg"
        />
    </div>
</template>

<style lang="scss"></style>
