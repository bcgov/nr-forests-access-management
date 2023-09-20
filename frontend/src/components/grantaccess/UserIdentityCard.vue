<script setup lang="ts">
import { toRaw } from 'vue';
import type { IdimProxyIdirInfo } from 'fam-api';
import Card from 'primevue/card';
import Icon from '../common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps<{
    userIdentity: IdimProxyIdirInfo;
}>(); // Vue3 alternative way for Type the defineProps().
console.log(toRaw(props.userIdentity))
</script>

<template>
    <Card class="mb-2 p-0">
        <template #header>
            <Icon icon="checkmark--filled" :size="IconSize.medium" />
            <p>Verified user information</p>
        </template>
        <template #content>
            <div class="col">
                <label class="row">User ID:</label>
                <span class="row">{{ props.userIdentity.userId }}</span>
            </div>
            <div class="col" v-if="props.userIdentity.found">
                <label class="row" >Display Name: </label>
                <span  class="row">{{ props.userIdentity.displayName }}</span>
            </div>
            <div class="col d-flex align-items-center" v-if="!props.userIdentity.found">
                <span class="px-0 invalid"> User does not exist </span>
            </div>
        </template>
    </Card>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

label {
    color: $light-text-primary;
    margin: 0 0 0.75rem !important;
}

span {
    margin: 0 !important;
    font-size: 0.875rem;
    line-height: 1.25rem;
    letter-spacing: 0.01rem;
}

.invalid {
    font-size: 0.875em;
    color: $light-text-error;
}
</style>
