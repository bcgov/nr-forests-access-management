<script setup lang="ts">
import { computed } from 'vue';
import InputText from 'primevue/inputtext';
import router from '@/router';
import { routeItems } from '@/router/routeItem';
import { IconSize } from '@/enum/IconEnum';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';

const props = defineProps({
    btnLabel: {
        type: String,
        required: true,
    },
    btnRoute: {
        type: String,
        required: true,
    },
    filter: {
        type: String,
        required: true,
    },
});
const emit = defineEmits(['change']);

const computedFilter = computed({
    get() {
        return props.filter;
    },
    set(newValue) {
        emit('change', newValue);
    },
});

const userLevelText = computed(() => {
    if (props.btnRoute == routeItems.grantDelegatedAdmin.path)
        return 'delegated admins';
    return 'users';
});
</script>

<template>
    <div class="custom-data-table-header">
        <h3>{{ selectedApplicationDisplayText }} {{ userLevelText }}</h3>
        <span>
            This table shows all the {{ userLevelText }} in
            {{ selectedApplicationDisplayText }} and their permissions levels
        </span>
    </div>

    <div class="search-container">
        <Button
            class="btn-add-user"
            :label="props.btnLabel"
            @click="router.push(props.btnRoute)"
        >
            <Icon icon="add" :size="IconSize.small" />
        </Button>
        <span class="p-input-icon-left">
            <Icon icon="search" :size="IconSize.small" />
            <InputText
                id="dashboardSearch"
                class="dash-search"
                placeholder="Search by keyword"
                v-model="computedFilter"
                :value="props.filter"
            />
        </span>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.custom-data-table-header {
    padding: 1rem 1rem 1.5rem;
    background-color: $light-layer-two;
    h3 {
        @extend %heading-03;
        margin: 0;
        padding: 0;
    }

    span {
        @extend %body-compact-01;
        margin: 0;
        padding: 0;
        color: $light-text-secondary;
    }
}

.search-container {
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
