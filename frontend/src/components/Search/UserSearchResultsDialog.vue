<script setup lang="ts">
import Button from "@/components/UI/Button.vue";
import { TABLE_DATATABLE_PT } from "@/passthrough/datatable/datatablePassThrough";
import type { SelectedUser } from "@/types/SelectUserType";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import type { Ref } from "vue";
import { computed, inject, nextTick, onMounted, ref } from "vue";


/**
 * This component is intended to be used as the content for user search results for the UserSearch component.
 * It is used within a PrimeVue DynamicDialog and receives data passed when opening the dialog,
 * as well as a close function to return results when the user confirms their selection.
 */

interface DialogRefData {
    data: { rows: SelectedUser[]; multiUserMode: boolean };
    close: (result?: SelectedUser[]) => void;
}

// PrimeVue DynamicDialog provides dialogRef as a Ref — must access via .value
const dialogRef = inject<Ref<DialogRefData>>("dialogRef");

const dataRows = computed(() => dialogRef?.value?.data?.rows ?? []);
const isMultiUserMode = computed(() => dialogRef?.value?.data?.multiUserMode ?? true);

const selectedDataRows = ref<SelectedUser[]>([]);
const selectedDataRow = ref<SelectedUser | null>(null);
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
            :pt="TABLE_DATATABLE_PT"
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
            :pt="TABLE_DATATABLE_PT"
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

// Group all nav buttons together — remove the auto-margin that splits « to the left
.search-results-table :deep(.fam-paginator .p-paginator-prev) {
    margin-left: 0;
}

// Center the nav button group within the paginator bar
.search-results-table :deep(.fam-paginator .fam-paginator-content) {
    justify-content: center;
}

// Light blue icon color for double-arrow (first/last) buttons
.search-results-table :deep(.fam-paginator .p-paginator-first),
.search-results-table :deep(.fam-paginator .p-paginator-last) {
    color: var(--semantic-color-primary-500);
}

// Darker blue for the active page number button
.search-results-table :deep(.fam-paginator .p-paginator-page.p-paginator-page-selected) {
    background-color: var(--semantic-color-primary-700);
    color: white;
}
</style>
