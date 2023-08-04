<script setup lang="ts">
import type { IdimProxyIdirInfo } from 'fam-api';
import Card from 'primevue/card';

const props = defineProps<{
    found: boolean,
    user: IdimProxyIdirInfo
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <Card class="mb-2 p-0">
        <template #content>
            <div class="row align-items-center">
                <label class="col-3">User ID:</label>
                <span class="col-sm">{{ props.user.userId }}</span>
            </div>
            <div class="row align-items-center"
                v-if="props.found">
                <label class="col-3">Display Name: </label>
                <span class="col-sm">{{ props.user.displayName }}</span>
            </div>
            <div class="row"
                v-if="!props.found">
                <span class="px-0 invalid">
                    User Does Not Exist
                </span>
            </div>
        </template>
    </Card>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.invalid {
    font-size: 0.875em;
    color: $fc-invalid-color;
}
</style>
