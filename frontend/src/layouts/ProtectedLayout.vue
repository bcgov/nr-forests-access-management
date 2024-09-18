<script setup lang="ts">
import type { ISideNavItem } from '@/components/common/SideNav.vue';
import Header from '@/components/header/Header.vue';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import sideNavData from '@/static/sideNav.json';
import {
    isApplicationSelected,
    selectedApplicationId,
} from '@/store/ApplicationState';
import { FAM_APPLICATION_ID } from '@/store/Constants';
import LoginUserState from '@/store/FamLoginUserState';
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const environmentSettings = new EnvironmentSettings();
const isDevEnvironment = environmentSettings.isDevEnvironment();
const navigationData = ref<[ISideNavItem]>(sideNavData as any);
const route = useRoute();

// Show and hide the correct sideNav btn based on the application
const setSideNavOptions = () => {
    if (selectedApplicationId.value === FAM_APPLICATION_ID) {
        disableSideNavOption('Add user permission', true);
        disableSideNavOption('Add application admin', false);
        if (isDevEnvironment) disableSideNavOption('Add delegated admin', true);
    } else {
        disableSideNavOption('Add application admin', true);
        disableSideNavOption('Add user permission', false);

        if (isDevEnvironment) {
            if (LoginUserState.isAdminOfSelectedApplication()) {
                disableSideNavOption('Add delegated admin', false);
            } else {
                disableSideNavOption('Add delegated admin', true);
            }
        }
    }
};

onMounted(() => {
    if (isApplicationSelected.value) {
        setSideNavOptions();
    }
});

// watch a ref:selectedApplicationId and a route change in order to react to sidNav difference.
watch([selectedApplicationId, route], () => {
    setSideNavOptions();
});

const disableSideNavOption = (optionName: string, disabled: boolean) => {
    const disableSideNavItemsOption = (optionName: string, disabled: boolean, items: ISideNavItem[]) => {
        items.forEach((navItem) => {
            if (navItem.name === optionName) {
                navItem.disabled = disabled;
            }
            if (navItem.items) {
                disableSideNavItemsOption(optionName, disabled, navItem.items);
            }
        })
    }

    disableSideNavItemsOption(optionName, disabled, navigationData.value);
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
