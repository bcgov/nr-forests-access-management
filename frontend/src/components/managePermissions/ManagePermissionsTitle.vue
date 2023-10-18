<script setup lang="ts">

const props = defineProps({
    isApplicationSelected: {
        type: Boolean,
        required: true,
        default: false,
    },
});
</script>

<template>
    <div class="row">
        <div class="col-6">
            <PageTitle
                title="Manage permissions"
                subtitle="Add permissions or edit users for the selected application"
            />
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';
div {
    width: auto;
}
</style>
