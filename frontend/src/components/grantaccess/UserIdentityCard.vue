<script setup lang="ts">
import Card from 'primevue/card';
import Icon from '@/components/common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';
import type { IdimProxyIdirInfo } from 'fam-app-acsctl-api';

const props = defineProps<{
    userIdentity: IdimProxyIdirInfo;
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <Card class="custom-card">
        <template #header>
            <Icon
                icon="checkmark--filled"
                :size="IconSize.small"
                v-if="props.userIdentity.found"
            />
            <Icon
                class="custom-carbon-icon-error--filled"
                icon="error--filled"
                :size="IconSize.small"
                v-else
            />
            <p>Verified user information</p>
        </template>
        <template #content>
            <div class="col" style="margin-left: 2rem">
                <label class="row">Username</label>
                <span class="row">{{ props.userIdentity.userId }}</span>
            </div>
            <div class="col" v-if="props.userIdentity.found">
                <label class="row">First Name</label>
                <span class="row">{{ props.userIdentity.firstName }}</span>
            </div>
            <div class="col" v-if="props.userIdentity.found">
                <label class="row">Last Name</label>
                <span class="row">{{ props.userIdentity.lastName }}</span>
            </div>
            <div
                class="col-6 d-flex"
                v-if="!props.userIdentity.found"
            >
                <span class="px-0 invalid"> User does not exist </span>
            </div>
        </template>
    </Card>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
@import '@/assets/styles/card.scss';
.col {
    margin-right: 0.5rem;
}
</style>
