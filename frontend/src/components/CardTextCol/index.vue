<!--
  CardTextCol Component
  This component is used to display a label and a description in a column format.
  It can show a loading skeleton when data is being fetched or processed.
-->
<script setup lang="ts">
import Skeleton from "primevue/skeleton";
import {
    PLACE_HOLDER,
    DEFAULT_SKELETON_BORDER_RADIUS,
} from "@/constants/constants";

const props = defineProps<{
    id: string;
    label: string;
    description?: string | null;
    isLoading?: boolean;
    hideDescription?: boolean;
}>();
</script>

<template>
    <div class="card-text-col-container">
        <div class="card-text-col-content">
            <span class="card-text-col-label" :id="`card-text-col-label-${id}`">
                {{ props.label }}
            </span>
            <Skeleton
                class="skeleton"
                width="8rem"
                :borderRadius="DEFAULT_SKELETON_BORDER_RADIUS"
                v-if="props.isLoading"
            />
            <!-- instead of a description you can use your own component here like a chip -->
            <slot v-else-if="hideDescription" />
            <span
                class="card-text-col-description"
                :id="`card-text-col-description-${id}`"
                v-else
            >
                {{ props.description ?? PLACE_HOLDER }}
            </span>
        </div>
    </div>
</template>

<style scoped lang="scss">
.card-text-col-container {
    padding-bottom: 0;
    min-width: fit-content;

    .card-text-col-content {
        display: flex;
        flex-direction: column;
        white-space: nowrap;

        .card-text-col-label {
            margin-bottom: 0.5rem;
            @include type.type-style("label-01");
            color: colors.$gray-100;
        }

        .card-text-col-description {
            @include type.type-style("body-01");
            color: colors.$gray-100;
        }
    }
}
</style>
