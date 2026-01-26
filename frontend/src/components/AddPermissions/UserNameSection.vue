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
        userList?: IdimProxyBceidInfoSchema[] | null;
        multiUserMode?: boolean;
    }>(),
    {
        fieldId: "user",
        multiUserMode: false,
        userList: () => [],
    }
);

const PERMISSION_REQUIRED_FOR_OPERATION = "permission_required_for_operation";


/**
 * Emits:
 * - addUser: In multi-user mode, requests parent to add a user to the user list.
 * - setUser: In single-user mode, notifies parent to set the verified user as the selected user.
 * - deleteUser: In multi-user mode, requests parent to remove a user from the user list.
 */
const emit = defineEmits(["addUser", "deleteUser", "setUser"]);


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
    errorMsg.value =
        "No user found. Check the spelling or try another username";
};



const addUserToList = (user: IdimProxyBceidInfoSchema) => {
    const list = props.userList ?? [];
    if (props.multiUserMode) {
        // In multi-user mode, emit addUser if not already present
        if (!list.some(u => u.userId === user.userId)) {
            emit("addUser", user);
        }
    } else {
        // In single-user mode, emit setUser to parent
        emit("setUser", user);
    }
};

const handleDeleteUser = (userId: string) => {
    emit("deleteUser", userId);
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
            addUserToList(data);
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
            addUserToList(data);
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
};

// whenver user domain change, remove the previous user identity card and clear input
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
            v-if="(props.userList ?? []).length > 0"
            :userList="props.userList ?? []"
            :multiUserMode="props.multiUserMode"
            @deleteUser="handleDeleteUser"
        />

        <div v-if="props.multiUserMode && (props.userList ?? []).length > 0" class="user-bulk-message-bar">
            <span>
                <b>{{ (props.userList ?? []).length }} user{{ (props.userList ?? []).length > 1 ? 's' : '' }}</b>
                &nbsp;will receive the same permissions configured below
            </span>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.verify-username-button {
    width: 12rem;
}

.user-bulk-message-bar {
    margin-top: 0.7rem;
    border: 1px solid #BEDBFF;
    background: #EFF6FF;
    color: #1C398E;
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-family: 'BC Sans', 'Noto Sans', Arial, sans-serif;
    font-size: 14px;
    font-weight: 400;
    display: flex;
    align-items: center;
    min-height: 38px;
    b {
        font-weight: 700;
    }
}
</style>
