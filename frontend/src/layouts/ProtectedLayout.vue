<script setup lang="ts">
import Header from '@/components/header/Header.vue';
import sideNavData from '@/static/sideNav.json';
import SideNav, { type ISideNavData } from '@/components/common/SideNav.vue';
import { ref, watch } from 'vue';
import { isApplicationSelected } from '@/store/ApplicationState';

const navigationData = ref<[ISideNavData]>(sideNavData as any);

watch(isApplicationSelected, (value) => {
    disableSideNavOption('Grant Access', !value);
});

function disableSideNavOption(optionName: string, disabled: boolean) {
    navigationData.value.map((item) => {
        item.items.map((child) => {
            if (child.name === optionName) {
                child.disabled = disabled;
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
