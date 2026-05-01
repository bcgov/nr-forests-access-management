<script setup lang="ts">
import Button from "@/components/UI/Button.vue";
import Dropdown from "@/components/UI/Dropdown.vue";
import HelperText from "@/components/UI/HelperText.vue";
import UserSearchResultsDialog from "@/components/Search/UserSearchResultsDialog.vue";
import { useUserSearchApiService } from "@/composables/useUserSearchApiService";
import type { UserSearchResultRow, UserSearchType } from "@/types/UserSearchTypes";
import SearchIcon from "@carbon/icons-vue/es/search/16";
import { UserType } from "fam-app-acsctl-api/model";
import type { DropdownChangeEvent } from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useDialog } from "primevue/usedialog";
import { computed, ref, watch } from "vue";

const searchText = ref("");
const searchTextError = ref("");
const searchResultMessage = ref("");
const latestConfirmedSelections = ref<UserSearchResultRow[]>([]);
const MAX_SEARCH_TEXT_LENGTH = 35;
const INVALID_SEARCH_TEXT_PATTERN_WITH_DIGITS = /[\s]/g; // no space (username allows digits)
const INVALID_SEARCH_TEXT_PATTERN = /[\s\d]/g; // no space, no numeric

interface SelectOption<T> {
    label: string;
    value: T;
}

interface Props {
    appId: number;
    availableDomains?: UserType[];
    disabled?: boolean;
    searchButtonLabel?: string;
}

const props = withDefaults(defineProps<Props>(), {
    availableDomains: () => [UserType.I, UserType.B],
    disabled: false,
    searchButtonLabel: "Search",
});

// Emits for parent component to react for changes in search.
const emit = defineEmits<{
    // Emitted when user changes selected domain, with new domain value
    "user-domain-change": [domain: UserType];
}>();

const dialog = useDialog();
const { searchUsers, isPending, searchResults, isSuccess, searchError, reset } =
    useUserSearchApiService();

const domainOptions = computed<SelectOption<UserType>[]>(() =>
    (props.availableDomains ?? []).map((domain) => ({
        label: domain === UserType.I ? "IDIR" : "BCeID",
        value: domain,
    }))
);

// Always default to the first domain option, and update if domainOptions change
const selectedDomainOption = ref<SelectOption<UserType>>(domainOptions.value[0]);
watch(domainOptions, (newOptions) => {
    if (!newOptions.length) return;
    // If current selection is not in new options, reset to first
    if (!newOptions.some(opt => opt.value === selectedDomainOption.value?.value)) {
        selectedDomainOption.value = newOptions[0];
    }
});

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

const openResultsDialog = (rows: UserSearchResultRow[]) => {
    dialog.open(UserSearchResultsDialog, {
        props: {
            modal: true,
            closable: true,
            style: { width: "85vw", "min-width": "52rem" },
        },
        data: { rows },
        onClose: (options) => {
            const selectedRows = options?.data as UserSearchResultRow[] | undefined;
            if (selectedRows && selectedRows.length > 0) {
                latestConfirmedSelections.value = selectedRows;
                // TODO: wire confirmed selections into add-permission form submission
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
            <HelperText
                v-if="searchResultMessage"
                :text="searchResultMessage"
                :is-error="true"
            />
            <slot name="searchError" />
        </div>
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
