<script setup lang="ts">
import { ref, watch, inject, type InjectionKey } from "vue";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import CheckmarkOutline from "@carbon/icons-vue/es/checkmark--outline/16";
import Button from "@/components/UI/Button.vue";
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
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import { useField } from "vee-validate";
import Label from "../UI/Label.vue";
import HelperText from "../UI/HelperText.vue";
import { formatUserNameAndId } from "@/utils/UserUtils";
import { SELECT_REGULAR_USER_KEY, type useSelectUserManagement } from "@/composables/useSelectUserManagement";
import type { SelectUser } from "@/types/SelectUserType";
import { toSelectUserManagementUser } from "@/composables/useSelectUserManagement";

const auth = useAuth();

interface Props {
    domain: UserType;
    appId: number;
    helperText: string;
    fieldId?: string;
    setIsVerifying?: (verifying: boolean) => void;
    injectionKey?: InjectionKey<ReturnType<typeof useSelectUserManagement>>;
}

const props = withDefaults(defineProps<Props>(), {
    fieldId: "user",
    injectionKey: () => SELECT_REGULAR_USER_KEY,
});

// Use useField to manage the user field
const { value: userFieldValue, errorMessage: userFieldError, setValue: setUserFieldValue } = useField<SelectUser | null>(props.fieldId);

// Inject the composable from parent
const grantUserManagement = inject(props.injectionKey);
if (!grantUserManagement) {
    console.error('UserNameSection: grantUserManagement composable not provided');
}

const PERMISSION_REQUIRED_FOR_OPERATION = "permission_required_for_operation";

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

/**
 * Add user to the composable's user list and update form field via useField.
 */
const addUserToList = (user: IdimProxyBceidInfoSchema | IdimProxyIdirInfoSchema) => {
    console.log("Adding user to list:", user);
    const selectUser = toSelectUserManagementUser(user);
    if (grantUserManagement) {
        grantUserManagement.addUser(selectUser);
    }
    setUserFieldValue(selectUser);
    userIdInput.value = ""; // Clear input after successful verification
};

/**
 * Delete user from the composable's user list.
 */
const handleDeleteUser = (userId: string) => {
    if (grantUserManagement) {
        grantUserManagement.deleteUser(userId);
    }
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

// whenever user domain changes, remove the previous user identity card and clear input
watch(
    () => props.domain,
    () => {
        userIdInput.value = "";
        resetsearchResult();
        // Clear composable state on domain change
        if (grantUserManagement) {
            grantUserManagement.clearUsers();
        }
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
        <div class="input-with-verify-button">
            <div>
                <InputText
                    id="userIdInput"
                    class="w-100 custom-height"
                    type="text"
                    maxlength="20"
                    v-model="userIdInput"
                    :class="{ 'is-invalid': userFieldError || errorMsg }"
                    @keydown.enter.prevent="handleVerify(props.domain)"
                    @blur="handleVerify(props.domain)"
                    :disabled="
                        verifyBceidMutation.isPending.value ||
                        verifyIdirMutation.isPending.value
                    "
                />
                <HelperText
                    :text="errorMsg || userFieldError || helperText"
                    :is-error="!!(userFieldError || errorMsg)"
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

        <!-- Merged: User Identity Table (formerly UserIdentityCard component) -->
        <div class="user-id-card-table" v-if="grantUserManagement && grantUserManagement.userList.value.length > 0">
            <div class="verified-message-bar">
                <CheckmarkOutline class="verified-icon" />
                <span class="verified-message-text">Verified user information</span>
            </div>
            <DataTable :value="Array.from(grantUserManagement.userList.value)" stripedRows class="user-table">
                <Column field="userId" header="Username" />
                <Column header="Full Name">
                    <template #body="{ data }">
                        {{ formatUserNameAndId(null, data.firstName, data.lastName) }}
                    </template>
                </Column>
                <Column field="email" header="Email" />
                <Column v-if="grantUserManagement.multiUserMode" header="" class="action-col">
                    <template #body="{ data }">
                        <button class="btn btn-icon" title="Delete user" @click="handleDeleteUser(data.userId)">
                            <TrashIcon />
                        </button>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Bulk message bar -->
        <div v-if="grantUserManagement && grantUserManagement.multiUserMode && grantUserManagement.userList.value.length > 0"
             class="user-bulk-message-bar">
            <span>
                <b>{{ grantUserManagement.userList.value.length }} user{{ grantUserManagement.userList.value.length > 1 ? 's' : '' }}</b>
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

// Merged styles from UserIdentityCard component
.user-id-card-table {
    margin-top: 2rem;
    .verified-message-bar {
        height: 38px;
        background: #F0FDF4;
        border: 1px solid #B9F8CF;
        display: flex;
        align-items: center;
        padding: 0 1rem;
        border-radius: 4px;
        margin-bottom: 0.7rem;
        font-family: 'BC Sans', 'Noto Sans', Arial, sans-serif;
        font-weight: 400;
        font-style: normal;
        font-size: 14px;
        color: #1a6333;
        .verified-icon {
            margin-right: 0.75rem;
            width: 20px;
            height: 20px;
            stroke: #008236;
        }
        .verified-message-text {
            display: inline-block;
            vertical-align: middle;
            color:#0D542B
        }
    }
    .user-table {
        width: 100%;
        .action-col {
            width: 48px;
            text-align: center;
        }
        .btn.btn-icon {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.25rem;
            display: flex;
            align-items: center;
            svg {
                width: 1rem;
                height: 1rem;
                color: inherit;
            }
        }
    }
}
</style>
