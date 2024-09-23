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

// const idpQuery = useQuery(
//     {
//         queryKey: [
//             'identity_search',
//             props.userTypeCode === 'I' ? 'idir' : 'bceid',
//             { user_id: props.userName, application_id: props.applicationId }
//         ],
//         queryFn:
//             props.userTypeCode === 'I'
//                 ? () => AppActlApiService.idirBceidProxyApi
//                     .idirSearch(
//                         props.userName,
//                         Number(props.applicationId),
//                     ).then((res) => res.data)
//                 : () => AppActlApiService.idirBceidProxyApi
//                     .bceidSearch(
//                         props.userName,
//                         Number(props.applicationId),
//                     ).then((res) => res.data),
//         enabled: props.userTypeCode === 'I' || props.userTypeCode === 'B'
//     }
// );

</script>

<template>

</template>

<style lang="scss">

</style>
