<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import Header from '@/components/header/Header.vue';
import SideNav, { type ISideNavItem } from '@/components/common/SideNav.vue';
import sideNavData from '@/static/sideNav.json';
import { FAM_APPLICATION_ID } from '@/store/Constants';
import {
    isApplicationSelected,
    selectedApplicationId,
} from '@/store/ApplicationState';
import LoginUserState from '@/store/FamLoginUserState';

const navigationData = ref<[ISideNavItem]>(sideNavData as any);

// Show and hide the correct sideNav btn based on the application
const setSideNavOptions = () => {
    if (selectedApplicationId.value === FAM_APPLICATION_ID) {
        disableSideNavOption('Add user permission', true);
        disableSideNavOption('Add application admin', false);
        disableSideNavOption('Add delegated admin', true);
    } else {
        disableSideNavOption('Add application admin', true);
        disableSideNavOption('Add user permission', false);

        if (LoginUserState.isAdminOfSelectedApplication()) {
            disableSideNavOption('Add delegated admin', false);
        } else {
            disableSideNavOption('Add delegated admin', true);
        }
    }
};

onMounted(() => {
    if (isApplicationSelected.value) {
        setSideNavOptions();
    }
});

watch(selectedApplicationId, () => {
    setSideNavOptions();
});

const disableSideNavOption = (optionName: string, disabled: boolean) => {
    navigationData.value.map((navItem) => {
        navItem.items?.map((childNavItem: ISideNavItem) => {
            if (childNavItem.name === optionName) {
                childNavItem.disabled = disabled;
            }
        });
    });
};
</script>
<template>
    <Header title="FAM" subtitle="Forests Access Management" />

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
