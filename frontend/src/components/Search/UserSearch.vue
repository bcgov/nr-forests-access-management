<script setup lang="ts">
import UserSearchResultsDialog from "@/components/Search/UserSearchResultsDialog.vue";
import UserSearchSelectedTable from "@/components/Search/UserSearchSelectedTable.vue";
import Button from "@/components/UI/Button.vue";
import Dropdown from "@/components/UI/Dropdown.vue";
import HelperText from "@/components/UI/HelperText.vue";
import { useUserSearchApiService } from "@/composables/useUserSearchApiService";
import type { SelectedUser } from "@/types/SelectUserType";
import type { UserSearchType } from "@/types/UserSearchTypes";
import SearchIcon from "@carbon/icons-vue/es/search/16";
import { UserType } from "fam-app-acsctl-api/model";
import type { DropdownChangeEvent } from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useDialog } from "primevue/usedialog";
import { computed, ref, watch } from "vue";

const searchText = ref(""); // user input value.
const searchTextError = ref(""); // error message for invalid search text
const searchResultMessage = ref(""); // message to display search result error or no results happens.
const latestConfirmedSelections = ref<SelectedUser[]>([]); // keep track of latest confirmed user selections.
const MAX_SEARCH_TEXT_LENGTH = 35; // limited to 35 although API allows up to 50.
const INVALID_SEARCH_TEXT_PATTERN_WITH_DIGITS = /[\s]/g; // no space (username allows digits)
const INVALID_SEARCH_TEXT_PATTERN = /[\s\d]/g; // no space, no numeric

interface SelectOption<T> {
    label: string;
    value: T;
}

interface Props {
    appId: number;
    multiUserMode: boolean; // multi user selection mode
    availableDomains?: UserType[];
    disabled?: boolean;
    searchButtonLabel?: string;
    helperText?: string; // helper text to show below search input, can be used to provide guidance.
}

const props = withDefaults(defineProps<Props>(), {
    availableDomains: () => [UserType.I, UserType.B],
    disabled: false,
    searchButtonLabel: "Search",
    helperText: "",
});

// Emits for parent component to react for changes in search.
const emit = defineEmits<{
    // Emitted when user changes selected domain, with new domain value
    "user-domain-change": [domain: UserType];
    "user-selection-update": [users: SelectedUser[]];
}>();

const dialog = useDialog();
// API service composable for user search to backend.
const { searchUsers, isPending, searchResults, isSuccess, searchError, reset } =
    useUserSearchApiService();

const selectedUsers = computed<readonly SelectedUser[]>(() =>
    latestConfirmedSelections.value
);

const isMultiUserMode = computed(() => props.multiUserMode);

const domainOptions = computed<SelectOption<UserType>[]>(() =>
    (props.availableDomains ?? []).map((domain) => ({
        label: domain === UserType.I ? "IDIR" : "BCeID",
        value: domain,
    }))
);

// Always default to the first domain option
const selectedDomainOption = ref<SelectOption<UserType>>(domainOptions.value[0]);

// Search by: "Username" for BCeID, and "First Name", "Last Name", or "Username" for IDIR
const getSearchTypeOptions = (
    domain: UserType
): SelectOption<UserSearchType>[] => {
    if (domain === UserType.B) {
        return [{ label: "Username", value: "username" }];
    }

    return [
        { label: "First Name", value: "firstName" },
        { label: "Last Name", value: "lastName" },
        { label: "Username", value: "username" },
    ];
};

const searchTypeOptions = computed<SelectOption<UserSearchType>[]>(() =>
    getSearchTypeOptions(selectedDomainOption.value.value)
);

const selectedSearchTypeOption = ref<SelectOption<UserSearchType>>(
    searchTypeOptions.value[0]
);

const isUsernameSearch = computed(
    () => selectedSearchTypeOption.value.value === "username"
);

/**
 * Test on search text. If contains invalid characters, return error msg.
 * - No space (always).
 * - No numeric (only for firstName/lastName searches).
 */
const getInvalidSearchTextError = (value: string): string => {
    if (/\s/.test(value)) {
        return "Search text cannot contain spaces";
    }

    if (!isUsernameSearch.value && /\d/.test(value)) {
        return "Search text cannot contain numbers";
    }

    return "";
};

const sanitizeSearchText = (value: string): string => {
    if (isUsernameSearch.value) {
        return value.replace(INVALID_SEARCH_TEXT_PATTERN_WITH_DIGITS, "");
    }
    return value.replace(INVALID_SEARCH_TEXT_PATTERN, "");
};

// This validates search text after 'searchText' model update.
const validateSearchText = (): boolean => {
    const trimmed = searchText.value.trim();

    if (!trimmed) {
        searchTextError.value = "Search text is required";
        return false;
    }

    if (trimmed.length > MAX_SEARCH_TEXT_LENGTH) {
        searchTextError.value = `Search text must be ${MAX_SEARCH_TEXT_LENGTH} characters or less`;
        return false;
    }

    const invalidSearchTextError = getInvalidSearchTextError(trimmed);
    if (invalidSearchTextError) {
        searchTextError.value = invalidSearchTextError;
        return false;
    }

    searchTextError.value = "";
    return true;
};

const clearSearchInputState = () => {
    searchText.value = "";
    searchTextError.value = "";
};

const handleDomainChange = (event: DropdownChangeEvent) => {
    const nextDomainOption = event.value as SelectOption<UserType>;
    if (!nextDomainOption || nextDomainOption.value === selectedDomainOption.value.value) {
        return;
    }

    selectedDomainOption.value = nextDomainOption;
    selectedSearchTypeOption.value = getSearchTypeOptions(nextDomainOption.value)[0];
    clearSearchInputState();
    searchResultMessage.value = "";
    reset();

    emit("user-domain-change", nextDomainOption.value);
};

const handleSearchTypeChange = (event: DropdownChangeEvent) => {
    const nextTypeOption = event.value as SelectOption<UserSearchType>;
    if (!nextTypeOption) {
        return;
    }

    selectedSearchTypeOption.value = nextTypeOption;
    clearSearchInputState();
    searchResultMessage.value = "";
    reset();
};

const handleBeforeModelUpdate = (event: InputEvent) => {
    if (!event.data) {
        return;
    }

    const invalidSearchTextError = getInvalidSearchTextError(event.data);
    if (!invalidSearchTextError) {
        return;
    }

    event.preventDefault(); // prevent invalid character from being entered into input
    searchTextError.value = invalidSearchTextError;
};

const handleSearchTextUpdate = (value: string | undefined) => {
    if (typeof value !== "string") {
        return;
    }

    const sanitizedValue = sanitizeSearchText(value);
    if (sanitizedValue !== value) {
        searchTextError.value = getInvalidSearchTextError(value);
        searchText.value = sanitizedValue;
        return;
    }

    searchText.value = value;

    if (searchTextError.value) {
        validateSearchText();
    }
};

const handlePaste = (event: ClipboardEvent) => {
    const pastedText = event.clipboardData?.getData("text") ?? "";
    const invalidSearchTextError = getInvalidSearchTextError(pastedText);
    if (invalidSearchTextError) {
        event.preventDefault();
        searchTextError.value = invalidSearchTextError;
    }
};

const syncSelectedUsers = (selectedDataRows: SelectedUser[]) => {
    latestConfirmedSelections.value = props.multiUserMode
        ? selectedDataRows
        : selectedDataRows.slice(0, 1);

    emit("user-selection-update", latestConfirmedSelections.value);
};

const handleDeleteSelectedUser = (userId: string) => {
    latestConfirmedSelections.value = latestConfirmedSelections.value.filter(
        (user) => user.userId.toLowerCase() !== userId.toLowerCase()
    );

    emit("user-selection-update", latestConfirmedSelections.value)
};

const openResultsDialog = (dataRows: SelectedUser[]) => {
    dialog.open(UserSearchResultsDialog, {
        props: {
            modal: true,
            closable: true,
            style: { width: "85vw", "min-width": "52rem" },
        },
        data: {
            rows: dataRows,
            multiUserMode: props.multiUserMode,
        },
        onClose: (options) => {
            const selectedDataRows = options?.data as SelectedUser[] | undefined;
            if (selectedDataRows && selectedDataRows.length > 0) {
                syncSelectedUsers(selectedDataRows);
            }
        },
    });
};

// Watch search results and react after a successful search
watch(isSuccess, (success) => {
    if (!success) return;

    const results = searchResults.value ?? [];
    if (results.length === 0) {
        searchResultMessage.value =
            "No search result found. Check the spelling or try another search.";
    } else {
        searchResultMessage.value = "";
        openResultsDialog(results);
    }
});

// Watch for API errors from the composable
watch(searchError, (err) => {
    if (err) {
        searchResultMessage.value = err;
    }
});

// Triggered when user clicks search button or presses Enter.
const handleSearch = () => {
    if (!validateSearchText()) {
        return;
    }

    searchResultMessage.value = "";

    searchUsers({
        domain: selectedDomainOption.value.value,
        searchType: selectedSearchTypeOption.value.value,
        searchText: searchText.value.trim(),
        appId: props.appId,
    });
};
</script>

<template>
    <div class="user-search-container">
        <div class="search-fields-row">
            <Dropdown
                class="field-domain"
                name="user-domain"
                label-text="User domain"
                option-label="label"
                :value="selectedDomainOption"
                :options="domainOptions"
                :on-change="handleDomainChange"
                :disabled="disabled || domainOptions.length === 1 || isPending"
            />

            <Dropdown
                class="field-type"
                name="search-type"
                label-text="Type"
                option-label="label"
                :value="selectedSearchTypeOption"
                :options="searchTypeOptions"
                :on-change="handleSearchTypeChange"
                :disabled="disabled || isPending"
            />

            <div class="field-search-input">
                <InputText
                    id="user-search-input"
                    :model-value="searchText"
                    @update:model-value="handleSearchTextUpdate"
                    @beforeinput="handleBeforeModelUpdate"
                    @keydown.space.prevent
                    @keydown.enter.prevent="handleSearch"
                    @paste="handlePaste"
                    placeholder="Please input search text"
                    :maxlength="MAX_SEARCH_TEXT_LENGTH"
                    class="w-100 custom-height"
                    :class="{ 'is-invalid': !!searchTextError }"
                    :disabled="disabled || isPending"
                />
                <HelperText
                    :text="searchTextError"
                    :is-error="!!searchTextError"
                />
            </div>

            <div class="field-search-button">
                <Button
                    :label="searchButtonLabel"
                    aria-label="Search users"
                    name="searchUsers"
                    outlined
                    :icon="SearchIcon"
                    :disabled="disabled"
                    :is-loading="isPending"
                    @click="handleSearch"
                />
            </div>
        </div>

        <div class="search-error-row">
            <!-- Helper text from parent component -->
            <HelperText
                v-if="helperText !== ''"
                :text="helperText"
            />
            <!-- Internal search result/error message -->
            <HelperText
                v-if="searchResultMessage"
                :text="searchResultMessage"
                :is-error="true"
            />
            <!-- Slot for additional form errors from parent component -->
            <slot name="formError" />
        </div>

        <UserSearchSelectedTable
            v-if="selectedUsers.length > 0"
            :users="selectedUsers"
            :multi-user-mode="isMultiUserMode"
            :on-delete-user="handleDeleteSelectedUser"
        />
    </div>
</template>

<style lang="scss" scoped>
.user-search-container {
    display: flex;
    flex-direction: column;
}


.search-fields-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
}


.field-domain,
.field-type {
    flex: 0 1 10rem;
    min-width: 10.5rem;
    min-height: 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

:deep(.fam-dropdown) {
    height: 2.5rem;
}


.field-search-input {
    flex: 1 1 16rem;
    min-width: 12rem;
    min-height: 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    margin-top: 1.5rem;
}


.field-search-button {
    flex: 0 0 auto;
    align-self: center;
    min-height: 2.5rem;
    display: flex;
    align-items: flex-end;
    margin-top: 1.5rem;
}

.search-error-row {
    width: 100%;
}

</style>
