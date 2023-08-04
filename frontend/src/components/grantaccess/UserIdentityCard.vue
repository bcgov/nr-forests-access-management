<script setup lang="ts">
import type { IdimProxyIdirInfo } from 'fam-api';
import Card from 'primevue/card';

const props = defineProps<{
    found: Boolean,
    user: IdimProxyIdirInfo
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <Card class="mb-2 p-0">
        <template #content>
            <div class="row">
                <label class="col-4">User ID:</label>
                <span class="col-sm">{{ props.user.userId }}</span>
            </div>
            <div class="row"
                v-if="props.found">
                <label class="col-4">Display Name: </label>
                <span class="col-sm">{{ props.user.displayName }}</span>
            </div>
            <div class="row"
                v-if="!props.found">
                <span class="invalid">
                    User Does Not Exist
                </span>
            </div>
        </template>
    </Card>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

label {
    line-height: 1.35rem;
}
.invalid {
    padding: 0;
    font-size: 0.875em;
    color: $fc-invalid-color;
}
</style>
