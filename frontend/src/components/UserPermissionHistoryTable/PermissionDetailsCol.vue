<script setup lang="ts">
import { formatForestClientDisplayName } from '@/utils/ForestClientUtils';
import { PrivilegeDetailsPermissionTypeEnum, PrivilegeDetailsScopeTypeEnum } from 'fam-app-acsctl-api/model';
import type { PrivilegeDetailsSchema } from 'fam-app-acsctl-api/model/privilege-details-schema';
import Chip from 'primevue/chip';

const props = defineProps<{
    permissionDetails: PrivilegeDetailsSchema;
    permissionChangeType: String;
}>();

enum PermissionChangeType {
    GRANT = 'GRANT',
    REVOKE = 'REVOKE'
};
</script>

<template>

    <!-- Details display for: permission Type change history as an 'EndUser' -->
    <div v-if="props.permissionDetails.permission_type === PrivilegeDetailsPermissionTypeEnum.EndUser"
        v-for="role in props.permissionDetails.roles" class="permission-details-col-container">
        <div class="permission-type-container">
            <p>Role: </p>
            <Chip :label="role.role" />
        </div>
        <div class="organizations-container" v-if="role.scopes?.find((scope) => scope !== null)">
            <p>Organizations:</p>
            <div class="organizations-list">
                <div v-for="scope in role.scopes">
                    <div v-if="scope && scope.scope_type === PrivilegeDetailsScopeTypeEnum.Client">
                        {{ formatForestClientDisplayName(scope.client_id, scope.client_name) }}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Details display for: permission Type change history as an 'DelegatedAdmin' -->
    <div v-if="props.permissionDetails.permission_type === PrivilegeDetailsPermissionTypeEnum.DelegatedAdmin">
        <div class="permission-type-container">
            <p>Role: </p>
            <Chip :label="props.permissionDetails.permission_type" />
        </div>
        <div v-for="role in props.permissionDetails.roles" class="permission-details-col-container">
            <div>
                <p>{{ props.permissionChangeType === PermissionChangeType.GRANT
                    ? 'Role enabled to assign:' : 'Role revoked from assignment:' }} {{ role.role }}</p>
            </div>
            <div class="organizations-container" v-if="role.scopes?.find((scope) => scope !== null)">
                <p>Organizations:</p>
                <div class="organizations-list">
                    <div v-for="scope in role.scopes">
                        <div v-if="scope && scope.scope_type === PrivilegeDetailsScopeTypeEnum.Client">
                            {{ formatForestClientDisplayName(scope.client_id, scope.client_name) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
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
.permission-details-col-container {
    display: flex;
    flex-direction: column;

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
