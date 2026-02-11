<script setup lang="ts">
import Button from "@/components/UI/Button.vue";
import useAuth from "@/composables/useAuth";
import { ADD_PERMISSION_SELECT_USER_KEY, toSelectUserManagementUser, type useSelectUserManagement } from "@/composables/useSelectUserManagement";
import { IdpProvider } from "@/enum/IdpEnum";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { formatUserNameAndId } from "@/utils/UserUtils";
import CheckmarkOutline from "@carbon/icons-vue/es/checkmark--outline/16";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import { useMutation } from "@tanstack/vue-query";
import type {
    IdimProxyBceidInfoSchema,
    IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api";
import { UserType } from "fam-app-acsctl-api";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { inject, ref, watch, type InjectionKey } from "vue";
import HelperText from "../UI/HelperText.vue";
import Label from "../UI/Label.vue";

const auth = useAuth();

interface Props {
    domain: UserType;
    appId: number;
    helperText: string;
    formValidateErrorMsg?: string;
    setIsVerifying?: (verifying: boolean) => void;
    injectionKey?: InjectionKey<ReturnType<typeof useSelectUserManagement>>;
}

const props = withDefaults(defineProps<Props>(), {
    injectionKey: () => ADD_PERMISSION_SELECT_USER_KEY,
});

const usernameInput = ref<string>(""); // input for username at this component.
const usernameVerificationErrorMsg = ref(""); // error message for username verification errors

// Inject select users composable from parent
const selectUserManagement = inject(props.injectionKey);

const PERMISSION_REQUIRED_FOR_OPERATION = "permission_required_for_operation";

/**
 * Checks if the provided user ID matches the currently logged-in user's ID.
 */
const isCurrentUser = (): boolean => {
    const userId = usernameInput.value?.toLowerCase();
    const loggedInUserId = auth.authState.famLoginUser?.username?.toLowerCase();
    return userId === loggedInUserId;
};

const handleMutationError = (error: any) => {
    usernameVerificationErrorMsg.value = "Failed to load username's data. Try verifying it again";
    // Check if error and response properties exist
    if (error.response && error.response.status === 403) {
        const detail = error.response.data?.detail;
        if (detail?.code === PERMISSION_REQUIRED_FOR_OPERATION) {
            usernameVerificationErrorMsg.value = `${detail.description}. Org name: ${
                auth.authState.famLoginUser?.organization ??
                "Unknown organization"
            }`;
        }
    }
};

const setUserNotFoundError = () => {
    usernameVerificationErrorMsg.value = "No user found. Check the spelling or try another username";
};

const addUserToList = (user: IdimProxyBceidInfoSchema | IdimProxyIdirInfoSchema) => {
    if (!selectUserManagement) return;
    const selectUser = toSelectUserManagementUser(user);
    // Check if user already exists in the list
    if (selectUserManagement.hasUser(selectUser.userId, selectUser.guid ?? undefined)) {
        usernameVerificationErrorMsg.value = "User has been added to the list";
        return;
    }
    selectUserManagement.addUser(selectUser);
    usernameInput.value = ""; // Clear input after successful verification
};

const handleDeleteUser = (userId: string) => {
    if (selectUserManagement) {
        selectUserManagement.deleteUser(userId);
    }
};

const verifyIdirMutation = useMutation({
    mutationFn: () => {
        if (props.setIsVerifying) {
            props.setIsVerifying(true);
        }
        return AppActlApiService.idirBceidProxyApi
            .idirSearch(usernameInput.value, props.appId)
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
            .bceidSearch(usernameInput.value, props.appId)
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
        !usernameInput.value
    ) {
        return;
    }
    if (isCurrentUser()) {
        usernameVerificationErrorMsg.value = "You cannot grant permissions to yourself.";
        return;
    }
    usernameVerificationErrorMsg.value = "";
    if (userType === "I") {
        verifyIdirMutation.mutate();
    }
    if (userType === "B") {
        verifyBceidMutation.mutate();
    }
};

const resetsearchResult = () => {
    usernameVerificationErrorMsg.value = "";
};

// whenever user domain changes, remove the previous user identity card and clear input
watch(
    () => props.domain,
    () => {
        usernameInput.value = "";
        resetsearchResult();
        // Clear composable state on domain change
        if (selectUserManagement) {
            selectUserManagement.clearUsers();
        }
    }
);
</script>

<template>
    <div class="form-field">
        <Label
            for="usernameInput"
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
                    id="usernameInput"
                    class="w-100 custom-height"
                    type="text"
                    maxlength="20"
                    v-model="usernameInput"
                    :class="{ 'is-invalid': usernameVerificationErrorMsg || formValidateErrorMsg }"
                    @keydown.enter.prevent="handleVerify(props.domain)"
                    :disabled="
                        verifyBceidMutation.isPending.value ||
                        verifyIdirMutation.isPending.value
                    "
                />
                <HelperText
                    :text="usernameVerificationErrorMsg || formValidateErrorMsg || helperText"
                    :is-error="!!(usernameVerificationErrorMsg || formValidateErrorMsg)"
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

        <!-- User Identity Table -->
        <div class="user-id-card-table" v-if="selectUserManagement && selectUserManagement.userList.value.length > 0">
            <div class="verified-message-bar">
                <CheckmarkOutline class="verified-icon" />
                <span class="verified-message-text">Verified user information</span>
            </div>
            <DataTable :value="Array.from(selectUserManagement.userList.value)" stripedRows class="user-table">
                <Column field="userId" header="Username" />
                <Column header="Full Name">
                    <template #body="{ data }">
                        {{ formatUserNameAndId(null, data.firstName, data.lastName) }}
                    </template>
                </Column>
                <Column field="email" header="Email" />
                <Column header="" class="action-col">
                    <template #body="{ data }">
                        <button class="btn btn-icon" title="Delete user" @click="handleDeleteUser(data.userId)">
                            <TrashIcon />
                        </button>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Bulk message bar -->
        <div v-if="selectUserManagement && selectUserManagement.multiUserMode && selectUserManagement.userList.value.length > 0"
             class="user-bulk-message-bar">
            <span>
                <b>{{ selectUserManagement.userList.value.length }} user{{ selectUserManagement.userList.value.length > 1 ? 's' : '' }}</b>
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
