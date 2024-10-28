<script setup lang="ts">
import TableHeaderTitle from "@/components/managePermissions/TableHeaderTitle.vue";
import type { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import {
    getTableHeaderDescription,
    getTableHeaderTitle,
} from "@/components/managePermissions/utils";

defineProps<{
    authGroup: AdminRoleAuthGroup;
    appName: string;
    appId: number;
}>();
</script>

<template>
    <div class="fam-table">
        <TableHeaderTitle
            :title="getTableHeaderTitle(appName, authGroup)"
            :description="getTableHeaderDescription(appName, authGroup)"
        />
    </div>
</template>
<style lang="scss" scoped>
.table-title-container {
}
</style>
