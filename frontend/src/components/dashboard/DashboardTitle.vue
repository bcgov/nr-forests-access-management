<script setup lang="ts">
import router from '@/router';
import { IconSize } from '@/enum/IconEnum';
import { loadingData } from '@/router/GrantAccessGuards';

const props = defineProps({
    isApplicationSelected: {
        type: Boolean,
        required: true,
        default: false,
    },
});

const handleClick = () => {
    loadingData.value = true;
    router.push('/grant');
};
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
                :label="loadingData ? 'Loading...' : 'Grant new access'"
                @click="handleClick"
            >
                <Icon icon="add" :size="IconSize.medium" />
            </Button>
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
