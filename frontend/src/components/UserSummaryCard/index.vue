<script setup lang="ts">
import { isAxiosError } from 'axios';
import { useQuery } from '@tanstack/vue-query';
import Card from 'primevue/card';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { DEFAULT_COL_SIZE, USER_TYPE_DESCRITION } from '@/components/UserSummaryCard/constants';
import CardTextCol from '@/components/CardTextCol/index.vue';

const props = defineProps<{
    userId: string; // Fam User ID
    applicationId: string
}>();

const userQuery = useQuery(
    {
        queryKey: ['fam_applications', props.applicationId, 'users', props.userId],
        queryFn: () => AppActlApiService.applicationsApi
            .getUserByUserId(Number(props.userId), Number(props.applicationId))
            .then((res) => res.data),
        enabled: !!props.userId && !!props.applicationId
    }
);

</script>

<template>
    <Card class="user-summary-card">
        <template #title>
            User Summary
        </template>
        <template #content v-if="userQuery.isError.value">
            Failed to fetch user info error.
            {{ isAxiosError(userQuery.error.value)
                ? `${userQuery.error.value.status} ${userQuery.error.value.message}`
                : null
            }}
        </template>
        <template #content v-else>
            <div class="grid">
                <CardTextCol :class="DEFAULT_COL_SIZE" id="user-name" label="Username"
                    :description="userQuery.data.value?.user_name" :is-loading="userQuery.isFetching.value" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="full-name" label="Full name"
                    :description="`${userQuery.data.value?.first_name} ${userQuery.data.value?.last_name}`"
                    :is-loading="userQuery.isFetching.value" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="domain" label="Domain"
                    :description="userQuery.data.value?.user_type.description"
                    :is-loading="userQuery.isFetching.value" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="email" label="Email"
                    :description="userQuery.data.value?.email" :is-loading="userQuery.isFetching.value" />
            </div>
        </template>
    </Card>
</template>

<style lang="scss">
.user-summary-card {
    border-radius: 0.5rem;

    .p-card-body {
        padding: 2rem;
    }

    .p-card-title {
        font-size: 1.25rem;
    }

    .p-card-content {
        padding-bottom: 0;
    }
}
</style>
