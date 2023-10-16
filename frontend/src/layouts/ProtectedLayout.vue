<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import Header from '@/components/header/Header.vue';
import SideNav, {
    type ISideNavData,
    type ISideNavItem,
} from '@/components/common/SideNav.vue';
import sideNavData from '@/static/sideNav.json';
import { isApplicationSelected } from '@/store/ApplicationState';
import { sideNavState } from '@/store/SideNavState'

const navigationData = ref<[ISideNavData]>(sideNavData as any);

onMounted(() => {
    disableSideNavOption('Grant Access', !isApplicationSelected.value);
});

watch(isApplicationSelected, (value) => {
    disableSideNavOption('Grant Access', !value);
});

const disableSideNavOption = (optionName: string, disabled: boolean) => {
    navigationData.value.map((navItem) => {
        navItem.items.map((childNavItem: ISideNavItem) => {
            if (childNavItem.name === optionName) {
                childNavItem.disabled = disabled;
            }
        });
    });
};

</script>
<template>
    <Header :title="sideNavState.isDesktopSize ? 'FAM Forestry Access Management' : 'FAM'" subtitle="Forests Access Management" />

    <SideNav :data="navigationData" />
    <div class="main">
        <main>
            <RouterView></RouterView>
        </main>
    </div>
</template>
<style lang="scss">
@import '@/assets/styles/base.scss';
</style>
