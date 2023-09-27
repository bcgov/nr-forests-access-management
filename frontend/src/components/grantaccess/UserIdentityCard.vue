<script setup lang="ts">
import type { IdimProxyIdirInfo } from 'fam-api';
import Card from 'primevue/card';
import Icon from '@/components/common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';

const props = defineProps<{
    userIdentity: IdimProxyIdirInfo;
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <Card class="mb-2 p-0 custom-card">
        <template #header>
            <Icon icon="checkmark--filled" :size="IconSize.small" />
            <p>Verified user information</p>
        </template>
        <template #content>
            <div class="col user-id">
                <label class="row">User ID:</label>
                <span class="row">{{ props.userIdentity.userId }}</span>
            </div>
            <div
                class="col"
                v-if="props.userIdentity.found"
            >
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

.user-id {
    margin-left: 2rem;
    margin-right: 2.5rem;
    flex-grow: 0;
}

.invalid {
    font-size: 0.875em;
    color: $light-text-error;
}
</style>
