<script setup lang="ts">
import type { IdimProxyIdirInfo } from 'fam-api';
import Card from 'primevue/card';

const props = defineProps<{
    found: Boolean,
    user: IdimProxyIdirInfo
}>(); // Vue3 alternative way for Type the defineProps().
</script>

<template>
    <div>
        <Card class="mb-2 p-0">
            <template #content>
                <div class="row">
                    <label>User ID:</label><span>{{ props.user.userId }}</span>
                </div>
                <div class="row"
                    v-if="props.found"
                >
                    <label>Display Name: </label><span
                        >{{ props.user.displayName }}</span
                    >
                </div>
            </template>
        </Card>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.invalid {
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #dc3545;
}
</style>
