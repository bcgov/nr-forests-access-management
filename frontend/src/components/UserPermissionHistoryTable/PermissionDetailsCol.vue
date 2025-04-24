<script setup lang="ts">
import Chip from "@/components/UI/Chip.vue";
import OrganizationsList from "@/components/UserPermissionHistoryTable/OrganizationList.vue";
import {
    PrivilegeChangeTypeEnum,
    PrivilegeDetailsPermissionTypeEnum,
} from "fam-app-acsctl-api/model";
import type { PrivilegeDetailsSchema } from "fam-app-acsctl-api/model/privilege-details-schema";

const props = defineProps<{
    permissionDetails: PrivilegeDetailsSchema;
    permissionChangeType: string;
}>();
</script>

<template>
    <!-- Details display for: permission Type change history as an 'EndUser' -->
    <div
        v-if="
            props.permissionDetails.permission_type ===
            PrivilegeDetailsPermissionTypeEnum.EndUser
        "
    >
        <div
            v-for="role in props.permissionDetails.roles"
            :key="role.role"
            class="permission-details-col-container"
        >
            <div class="permission-type-container">
                <p>Role:</p>
                <Chip :label="role.role" />
            </div>
            <OrganizationsList
                v-if="role.scopes?.find((scope) => scope !== null)"
                :scopes="role.scopes"
            />
        </div>
    </div>

    <!-- Details display for: permission Type change history as an 'DelegatedAdmin' -->
    <div
        v-if="
            props.permissionDetails.permission_type ===
            PrivilegeDetailsPermissionTypeEnum.DelegatedAdmin
        "
    >
        <div class="permission-type-container">
            <p>Role:</p>
            <Chip :label="props.permissionDetails.permission_type" />
        </div>
        <div
            v-for="role in props.permissionDetails.roles"
            :key="role.role"
            class="permission-details-col-container"
        >
            <div class="d-admin-role-container">
                <p>
                    {{
                        props.permissionChangeType ===
                        PrivilegeChangeTypeEnum.Grant
                            ? "Role enabled to assign:"
                            : "Role revoked from assignment:"
                    }}
                    {{ role.role }}
                </p>
            </div>
            <OrganizationsList
                v-if="role.scopes?.find((scope) => scope !== null)"
                :scopes="role.scopes"
            />
        </div>
    </div>

    <!-- Details display for: permission Type change history as an 'ApplicationAdmin' -->
    <div
        v-if="
            props.permissionDetails.permission_type ===
            PrivilegeDetailsPermissionTypeEnum.ApplicationAdmin
        "
    >
        <div class="permission-type-container">
            <p>Role:</p>
            <Chip :label="props.permissionDetails.permission_type" />
        </div>
    </div>
</template>

<style lang="scss">
.permission-type-container {
    display: flex;
    flex-direction: row;

    .fam-chip {
        margin-left: 0.5rem;
    }
}

.permission-details-col-container {
    display: flex;
    flex-direction: column;

    .d-admin-role-container {
        margin-top: 0.5rem;
    }
}
</style>
