<script setup lang="ts">
import MyPermissionsTable from '@/components/myPermissions/MyPermissionsTable.vue';
import PageTitle from '@/components/common/PageTitle.vue';
</script>

<template>
    <PageTitle
        title="My permissions"
        subtitle="Check all the applications and permissions that you have access to"
    />
    <MyPermissionsTable />
</template>
