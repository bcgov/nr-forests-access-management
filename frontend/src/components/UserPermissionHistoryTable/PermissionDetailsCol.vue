<script setup lang="ts">
import Chip from 'primevue/chip';
import { formatForestClientDisplayName } from '@/utils/ForestClientUtils';
import type { PrivilegeDetailsSchema } from 'fam-app-acsctl-api/model/privilege-details-schema';

const props = defineProps<{
    permissionDetails: PrivilegeDetailsSchema;
}>();

</script>

<template>
    <div v-for="role in props.permissionDetails.roles" class="permission-details-col-container">
        <div class="permission-type-container">
            <p>Role: </p>
            <Chip :label="role.role" />
        </div>
        <div class="organizations-container" v-if="role.scopes?.find((scope) => scope !== null)">
            <p>Organizations:</p>
            <div class="organizations-list">
                <br />
                <div v-for="scope in role.scopes">
                    <div v-if="scope && scope.scope_type === 'Client'">
                        {{ formatForestClientDisplayName(scope.client_id, scope.client_name) }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.permission-details-col-container {
    display: flex;
    flex-direction: column;

    .permission-type-container {
        display: flex;
        flex-direction: row;

        .p-chip {
            max-height: 1.5rem;
            background: colors.$blue-10;
            margin-left: 0.5rem;
        }

        .p-chip-text {
            @include type.type-style('label-01');
            color: colors.$blue-80;
        }
    }

    .organizations-container {
        display: flex;
        flex-direction: row;
        margin-top: 0.5rem;

        .organizations-list {
            margin-left: 0.5rem;
        }
    }
}
</style>
