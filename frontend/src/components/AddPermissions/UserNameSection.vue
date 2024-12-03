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
import { Field } from "vee-validate";
import Label from "../UI/Label.vue";
import HelperText from "../UI/HelperText.vue";

const auth = useAuth();

const props = withDefaults(
    defineProps<{
        domain: UserType;
        user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null;
        appId: number;
        helperText: string;
        fieldId?: string;
        setIsVerifying?: (verifying: boolean) => void;
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

    errorMsg.value = "Failed to load username's data. Try verifying it again";

    // Check if error and response properties exist
    if (error.response && error.response.status === 403) {
        const detail = error.response.data?.detail;
        if (detail?.code === PERMISSION_REQUIRED_FOR_OPERATION) {
            errorMsg.value = `${detail.description}. Org name: ${
                auth.authState.famLoginUser?.organization ??
                "Unknown organization"
            }`;
        }
    }
};

const setUserNotFoundError = () => {
    emit("setVerifyResult", null);
    errorMsg.value =
        "No user found. Check the spelling or try another username";
};

const verifyIdirMutation = useMutation({
    mutationFn: () => {
        if (props.setIsVerifying) {
            props.setIsVerifying(true);
        }
        return AppActlApiService.idirBceidProxyApi
            .idirSearch(userIdInput.value, props.appId)
            .then((res) => res.data);
    },
    onSuccess: (data) => {
        if (data.found) {
            emit("setVerifyResult", data);
        } else {
            setUserNotFoundError();
        }
    },
    onError: (error) => handleMutationError(error),
    onSettled: () => {
        if (props.setIsVerifying) {
            props.setIsVerifying(false);
        }
    },
});

const verifyBceidMutation = useMutation({
    mutationFn: () => {
        if (props.setIsVerifying) {
            props.setIsVerifying(true);
        }
        return AppActlApiService.idirBceidProxyApi
            .bceidSearch(userIdInput.value, props.appId)
            .then((res) => res.data);
    },
    onSuccess: (data) => {
        if (data.found) {
            emit("setVerifyResult", data);
        } else {
            setUserNotFoundError();
        }
    },
    onError: (error) => handleMutationError(error),
    onSettled: () => {
        if (props.setIsVerifying) {
            props.setIsVerifying(false);
        }
    },
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
        <Label
            for="userIdInput"
            :label-text="`Username (${
                props.domain === UserType.I
                    ? IdpProvider.IDIR
                    : IdpProvider.BCEIDBUSINESS
            })`"
            required
        />
        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            v-model="props.user"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="userIdInput"
                        class="w-100 custom-height"
                        type="text"
                        maxlength="20"
                        v-model="userIdInput"
                        :class="{ 'is-invalid': errorMessage || errorMsg }"
                        @keydown.enter.prevent="handleVerify(props.domain)"
                        @blur="handleVerify(props.domain)"
                        :disabled="
                            verifyBceidMutation.isPending.value ||
                            verifyIdirMutation.isPending.value
                        "
                    />
                    <HelperText
                        :text="errorMsg || errorMessage || helperText"
                        :is-error="!!(errorMessage || errorMsg)"
                    />
                </div>

                <Button
                    class="verify-username-button"
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
                    label="Verify username"
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

<style lang="scss" scoped>
.verify-username-button {
    width: 12rem;
}
</style>
