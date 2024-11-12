<script setup lang="ts">
import MyPermissionsTable from "@/components/MyPermissionsTable";
import PageTitle from "@/components/UI/PageTitle.vue";
</script>

<template>
    <div class="my-permissions-container">
        <PageTitle
            title="My permissions"
            subtitle="Check all the applications and permissions that you have access to"
        />
        <MyPermissionsTable />
    </div>
</template>

<style lang="scss">
.my-permissions-container {
    .my-permissions-table-container {
        margin-top: 3rem;
    }
}
</style>
