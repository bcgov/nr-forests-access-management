<script setup lang="ts">
import { computed } from "vue";
import InputText from "primevue/inputtext";
import { hashRouter } from "@/router";
import { routeItems } from "@/router/RouteItems";
import { IconSize } from "@/enum/IconEnum";
import { selectedApplicationDisplayText } from "@/store/ApplicationState";

const props = defineProps({
    btnLabel: {
        type: String,
        required: false,
    },
    btnRoute: {
        type: String,
        required: false,
    },
    filter: {
        type: String,
        required: true,
    },
    hasHeader: {
        type: Boolean,
        default: true,
        required: false,
    },
    inputPlaceholder: {
        type: String,
        default: "Search by keyword",
        required: false,
    },
});
const emit = defineEmits(["change"]);

const computedFilter = computed({
    get() {
        return props.filter;
    },
    set(newValue) {
        emit("change", newValue);
    },
});

const userLevelText = "TODO";
//  computed(() => {
//     if (props.btnRoute == routeItems.grantDelegatedAdmin.path)
//         return "delegated administrators";
//     return "users";
// });

const tableHeaderCustomText = "TODO";
//  computed(() => {
//     if (props.btnRoute == routeItems.grantDelegatedAdmin.path)
//         return "and the roles they are allowed to manage for their users";
//     return "and their permissions levels";
// });
</script>

<template>
    <div class="custom-data-table-header" v-if="props.hasHeader">
        <h3>{{ selectedApplicationDisplayText }} {{ userLevelText }}</h3>
        <p aria-roledescription="subtitle">
            This table shows all the {{ userLevelText }} in
            {{ selectedApplicationDisplayText }} {{ tableHeaderCustomText }}
        </p>
    </div>

    <div class="utility-container">
        <Button
            v-if="props.btnRoute"
            class="btn-add-user"
            :label="props.btnLabel"
            @click="hashRouter.push(props.btnRoute)"
        >
            <Icon icon="add" :size="IconSize.small" />
        </Button>
        <span class="p-input-icon-left">
            <Icon icon="search" :size="IconSize.small" />
            <InputText
                id="dashboardSearch"
                class="dash-search"
                :placeholder="props.inputPlaceholder"
                v-model="computedFilter"
                :value="props.filter"
            />
        </span>
    </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/base.scss";

.custom-data-table-header {
    padding: 1rem 1rem 1.5rem;
    background-color: $light-layer-two;

    h3 {
        @extend %heading-03;
        margin: 0;
        padding: 0;
    }

    p {
        @extend %body-compact-01;
        margin: 0;
        padding: 0;
        color: $light-text-secondary;
    }
}

.utility-container {
    display: flex;
}

.btn-add-user {
    width: 16rem;
    z-index: 2;
    border-radius: 0rem;
}

.dash-search {
    border-radius: 0 0 0 0;
}

// update primevue style but only for FAM
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

:deep(.p-datatable .p-sortable-column .p-sortable-column-icon) {
    display: none;
}
</style>
