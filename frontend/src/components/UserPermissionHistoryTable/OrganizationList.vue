<script setup lang="ts">
import { formatForestClientDisplayName } from '@/utils/ForestClientUtils';
import type { PrivilegeDetailsScopeSchema } from 'fam-app-acsctl-api/model';
import { PrivilegeDetailsScopeTypeEnum } from 'fam-app-acsctl-api/model';

const props = defineProps<{
    scopes: PrivilegeDetailsScopeSchema[];
}>();
</script>

<template>
    <div class="organizations-container">
        <p>Organizations:</p>
        <div class="organizations-list">
            <div v-for="(scope, index) in props.scopes" :key="index">
                <div v-if="scope && scope.scope_type === PrivilegeDetailsScopeTypeEnum.Client">
                    {{ formatForestClientDisplayName(scope.client_id, scope.client_name) }}
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.organizations-container {
    display: flex;
    flex-direction: row;
    margin-top: 0.5rem;

    .organizations-list {
        margin-left: 0.5rem;
    }
}
</style>
