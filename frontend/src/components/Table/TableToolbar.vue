<script setup lang="ts">
import { computed, ref } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import AddIcon from "@carbon/icons-vue/es/add/16";
import SearchIcon from "@carbon/icons-vue/es/search/16";

const props = defineProps<{
    filter: string;
    inputPlaceholder: string;
    btnLabel?: string;
    btnOnClick?: Function;
    errorMessage?: string | null;
}>();

const emit = defineEmits(["change", "blur"]);

// Track the previous value of the filter
const previousFilter = ref(props.filter);

const computedFilter = computed({
    get() {
        return props.filter;
    },
    set(newValue) {
        emit("change", newValue);
    },
});

const handleBlur = () => {
    const isChanged = props.filter !== previousFilter.value;
    if (isChanged) {
        previousFilter.value = props.filter;
    }
    emit("blur", props.filter, isChanged);
};
</script>

<template>
    <div class="toolbar-container">
        <Button
            v-if="btnOnClick && btnLabel"
            class="action-button"
            @click="btnOnClick!"
        >
            <span>{{ btnLabel }}</span>
            <AddIcon />
        </Button>
        <span class="p-input-icon-left">
            <SearchIcon />
            <InputText
                id="dashboardSearch"
                class="dash-search"
                :placeholder="inputPlaceholder"
                v-model="computedFilter"
                :value="filter"
                @blur="handleBlur"
                @keydown.enter.prevent="handleBlur"
            />
        </span>
    </div>
</template>

<style lang="scss" scoped>
.toolbar-container {
    display: flex;

    .action-button {
        width: 16rem;
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
