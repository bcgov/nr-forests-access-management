<script setup lang="ts">
import { useRoute } from 'vue-router';
import Breadcrumb from 'primevue/breadcrumb';
import Steps from 'primevue/steps';
import Icon from '@/components/common/Icon.vue';
import { breadcrumbState } from '@/store/BreadcrumbState';
import { stepItems } from '@/store/stepState';
import { IconSteps } from '@/enum/IconEnum';
import type { MenuItem } from 'primevue/menuitem';

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: true,
    }
});

const route = useRoute();

const isActive = (item: MenuItem) => {
    return item.active;
};

const iconClass = (item: MenuItem) => {
    if(item.icon === IconSteps.incomplete) {
        return '';
    } else if(item.icon === IconSteps.warning) {
        return 'inactive invalid';
    } else if (!item.active) {
        return 'inactive';
    };
};

</script>

<template>
    <Breadcrumb
        v-if="route.meta.hasBreadcrumb"
        :model="breadcrumbState"
    />
    <h1 class="title">{{ props.title }}</h1>
    <h2 class="subtitle">{{ props.subtitle }}</h2>
    <Steps
        v-if="route.meta.hasSteps && stepItems"
        :readonly="false"
        :model="stepItems" aria-label="Form Steps"
        :pt="{
            menuitem: ({ context }) => ({
                class: isActive(context.item) && 'p-highlight p-steps-current'
            })
        }"
    >
        <template #item="{ item, index }">
            <span v-if="item" class="custom-steps">
                <Icon
                    :icon="item.icon!"
                    :class="iconClass(item)"
                />
                <div>
                    <p>{{ item.label }}</p>
                    <p :class="iconClass(item)">{{
                        item.errorMessage ? item.errorMessage : `step ${ index + 1 }`}}</p>
                </div>
            </span>
        </template>
    </Steps>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
p {
    font-size: 0.875rem;
    letter-spacing: 0.01rem;
    margin: 0;
}

svg {
        color: $light-interactive;
        margin: 0.15rem 0.5rem 0 0;
}

.custom-step-index {
    font-size: 0.75rem;
    color: $light-text-secondary;
}
.title {
    font-size: 2rem;
    line-height: 2.5rem;
    color: $light-text-primary;
    font-weight: 400;
}

.subtitle {
    font-size: 0.875rem;
    line-height: 1.125rem;
    letter-spacing: 0.01rem;
    color: $light-text-secondary;
}

.custom-steps {
    display: flex;
    margin-top: 0.5rem;
}

.inactive {
    color: $light-text-primary;
}

.invalid {
    color: red !important;
}
</style>
