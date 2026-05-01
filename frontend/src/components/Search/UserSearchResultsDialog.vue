<script setup lang="ts">
import Button from "@/components/UI/Button.vue";
import type { UserSearchResultRow } from "@/types/UserSearchTypes";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { computed, inject, nextTick, onMounted, ref } from "vue";
import type { Ref } from "vue";

/**
 * This component is intended to be used as the content for user search results for the UserSearch component.
 * It is used within a PrimeVue DynamicDialog and receives data passed when opening the dialog,
 * as well as a close function to return results when the user confirms their selection.
 */

interface DialogRefData {
    data: { rows: UserSearchResultRow[]; multiUserMode: boolean };
    close: (result?: UserSearchResultRow[]) => void;
}

// PrimeVue DynamicDialog provides dialogRef as a Ref — must access via .value
const dialogRef = inject<Ref<DialogRefData>>("dialogRef");

const dataRows = computed(() => dialogRef?.value?.data?.rows ?? []);
const isMultiUserMode = computed(() => dialogRef?.value?.data?.multiUserMode ?? true);

const selectedDataRows = ref<UserSearchResultRow[]>([]);
const selectedDataRow = ref<UserSearchResultRow | null>(null);
const tableRef = ref();

const handleConfirm = () => {
    if (isMultiUserMode.value) {
        dialogRef?.value?.close(selectedDataRows.value);
        return;
    }

    dialogRef?.value?.close(selectedDataRow.value ? [selectedDataRow.value] : []);
};

onMounted(async () => {
    // Wait for the table to render then set auto-focus on the first checkbox/radio input for better UX when dialog opens.
    await nextTick();
    const el = tableRef.value?.$el as HTMLElement | undefined;
    const firstSelectionInput = el?.querySelector('input[type="checkbox"], input[type="radio"]') as HTMLInputElement | null;
    firstSelectionInput?.focus();

    // Auto-select if only one row
    if (dataRows.value.length === 1) {
        if (isMultiUserMode.value) {
            selectedDataRows.value = [dataRows.value[0]];
        } else {
            selectedDataRow.value = dataRows.value[0];
        }
    }
});
</script>


<template>
    <div class="search-results-dialog-content">
        <div class="dialog-header-row">
            <h2 class="search-results-title">User Search Results</h2>
            <Button
                type="submit"
                label="Confirm"
                name="confirm-search-results"
                class="confirm-btn"
                :disabled="isMultiUserMode ? selectedDataRows.length === 0 : !selectedDataRow"
                @click="handleConfirm"
            />
        </div>

        <DataTable
            v-if="isMultiUserMode"
            ref="tableRef"
            v-model:selection="selectedDataRows"
            :value="dataRows"
            striped-rows
            paginator
            :rows="10"
            :rows-per-page-options="[10, 20, 50, 100]"
            class="search-results-table"
        >
            <Column selection-mode="multiple" header-style="width: 3rem" />
            <Column field="userId" header="Username" />
            <Column field="firstName" header="First name" />
            <Column field="lastName" header="Last name" />
            <Column field="email" header="Email" />
        </DataTable>

        <DataTable
            v-else
            ref="tableRef"
            v-model:selection="selectedDataRow"
            selection-mode="single"
            :value="dataRows"
            striped-rows
            paginator
            :rows="10"
            :rows-per-page-options="[10, 20, 50, 100]"
            class="search-results-table"
        >
            <Column selection-mode="single" header-style="width: 3rem" />
            <Column field="userId" header="Username" />
            <Column field="firstName" header="First name" />
            <Column field="lastName" header="Last name" />
            <Column field="email" header="Email" />
        </DataTable>
    </div>
</template>

<style lang="scss" scoped>

.search-results-dialog-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.search-results-title {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    text-align: left;
}


.dialog-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    margin-top: 0.5rem;
}

.search-results-table {
    width: 100%;
}

:deep(.confirm-btn.fam-button) {
    max-width: 6rem;
}
:deep(.fam-button .button-content) {
    margin-left: 7px;
}
</style>
