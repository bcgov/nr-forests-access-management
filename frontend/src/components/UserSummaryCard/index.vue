<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';
import { AppActlApiService } from '@/services/ApiServiceFactory';
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
                    )
                : () => AppActlApiService.idirBceidProxyApi
                    .bceidSearch(
                        props.userName,
                        Number(props.applicationId),
                    ),
        enabled: props.userTypeCode === 'I' || props.userTypeCode === 'B'
    } // TODO default caching
);

</script>

<template>
    <div>
        <p>User Name: {{ props.userName }}</p>
        <p>User Type Code: {{ props.userTypeCode }}</p>
    </div>
</template>

<style scoped lang="scss">
@import '@/assets/styles/base.scss';
</style>
