<script setup lang="ts">
import { computed } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import AddIcon from "@carbon/icons-vue/es/add/16";
import SearchIcon from "@carbon/icons-vue/es/search/16";

const props = defineProps<{
    filter: string;
    btnLabel?: string;
    btnOnClick?: Function;
    inputPlaceholder: string;
}>();

const emit = defineEmits(["change"]);

const computedFilter = computed({
    get() {
        return props.filter;
    },
    set(newValue) {
        emit("change", newValue);
    },
});
</script>

<template>
    <div class="toolbar-container">
        <Button
            v-if="btnOnClick && btnLabel"
            class="action-button"
            :label="btnLabel"
            @click="btnOnClick!"
        >
            {{ btnLabel }}
            <template #icon>
                <AddIcon />
            </template>
        </Button>
        <span class="p-input-icon-left">
            <SearchIcon />
            <InputText
                id="dashboardSearch"
                class="dash-search"
                :placeholder="inputPlaceholder"
                v-model="computedFilter"
                :value="filter"
            />
        </span>
    </div>
</template>

<style lang="scss" scoped>
.toolbar-container {
    display: flex;

    .action-button {
        width: 16rem;
        z-index: 2;
        border-radius: 0rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }

    .dash-search {
        border-radius: 0 0 0 0;
    }

    .p-input-icon-left {
        z-index: 1;
        flex-grow: 1;

        svg {
            top: 52%;
        }

        &:deep(.p-inputtext) {
            width: 100%;
            border-bottom: 0.125rem solid transparent;
        }

        &:deep(.p-inputtext:hover) {
            border-bottom: 0.125rem solid transparent;
        }
    }
}
</style>
