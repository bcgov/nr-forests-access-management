<script setup lang="ts">
import router from '@/router';

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
            <PageTitle title="Dashboard" subtitle="Manage permissions" />
        </div>
        <div class="col-6">
            <Button
                v-if="props.isApplicationSelected"
                class="dashboard-button"
                label="Grant new access"
                @click="router.push('/grant')"
                ><Icon icon="AddIcon" medium class="icon-size-1"
            /></Button>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

.dashboard-button {
    width: 14.6875rem;
    float: right;
}
</style>
