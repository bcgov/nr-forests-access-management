<script setup lang="ts">
import { isAxiosError } from 'axios';
import { useQuery } from '@tanstack/vue-query';
import Card from 'primevue/card';
import { AppActlApiService } from '@/services/ApiServiceFactory';
import { DEFAULT_COL_SIZE, USER_TYPE_DESCRITION } from '@/components/UserSummaryCard/constants';
import CardTextCol from '@/components/CardTextCol/index.vue';

import type { UserTypeCodeType } from '@/types/UserTypeCodeType';

const props = defineProps<{
    userName: string;
    userTypeCode: UserTypeCodeType
    applicationId: string
}>();

const idpQuery = useQuery(
    {
        queryKey: [
            'identity_search',
            props.userTypeCode === 'I' ? 'idir' : 'bceid',
            { user_id: props.userName, application_id: props.applicationId }
        ],
        queryFn:
            props.userTypeCode === 'I'
                ? () => AppActlApiService.idirBceidProxyApi
                    .idirSearch(
                        props.userName,
                        Number(props.applicationId),
                    ).then((res) => res.data)
                : () => AppActlApiService.idirBceidProxyApi
                    .bceidSearch(
                        props.userName,
                        Number(props.applicationId),
                    ).then((res) => res.data),
        enabled: props.userTypeCode === 'I' || props.userTypeCode === 'B'
    }
);

</script>

<template>
    <Card class="user-summary-card">
        <template #title>
            User Summary
        </template>
        <template #content v-if="idpQuery.isError.value">
            Failed to fetch user info error.
            {{ isAxiosError(idpQuery.error.value)
                ? `${idpQuery.error.value.status} ${idpQuery.error.value.message}`
                : null
            }}
        </template>
        <template #content v-else>
            <div class="grid">
                <CardTextCol :class="DEFAULT_COL_SIZE" id="user-name" label="Username" :description="userName" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="full-name" label="Full name"
                    :description="`${idpQuery.data.value?.firstName} ${idpQuery.data.value?.lastName}`"
                    :isLoading="idpQuery.isFetching.value" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="domain" label="Domain"
                    :description="USER_TYPE_DESCRITION[userTypeCode]" />

                <CardTextCol :class="DEFAULT_COL_SIZE" id="email" label="Email"
                    :description="idpQuery.data.value?.email" :isLoading="idpQuery.isFetching.value" />
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
