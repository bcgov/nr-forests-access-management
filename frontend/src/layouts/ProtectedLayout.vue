<script setup lang="ts">
import { ref, watch } from 'vue';
import Header from '@/components/header/Header.vue';
import SideNav, { type ISideNavData } from '@/components/common/SideNav.vue';
import sideNavData from '@/static/sideNav.json';
import { isApplicationSelected } from '@/store/ApplicationState';

const navigationData = ref<[ISideNavData]>(sideNavData as any);

watch(isApplicationSelected, (value) => {
    disableSideNavOption('Grant Access', !value);
});

function disableSideNavOption(optionName: string, disabled: boolean) {
    navigationData.value.map((navItem) => {
        navItem.items.map((childNavItem) => {
            if (childNavItem.name === optionName) {
                childNavItem.disabled = disabled;
            }
        });
    });
}
</script>
<template>
    <Header title="FAM" subtitle="Forest Access Management" />

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
