<script setup lang="ts">
import type { PropType } from 'vue';
import router from '@/router';
import type { RouteLocationRaw } from 'vue-router';

interface ISideNavData {
    name: string;
    items: [ISideNavItem];
}

interface ISideNavItem {
    name: string;
    icon: string;
    link: RouteLocationRaw;
    disabled: boolean;
}

const props = defineProps({
    data: {
        type: Object as PropType<ISideNavData[]>,
        required: true,
        default: '',
    },
});

</script>
<template>
    <nav class="p-sidenav">
        <a
            class="p-sidenav-logo"
            title="Forest Access Management"
            href="https://www2.gov.bc.ca"
        >
            <img
                src="@/assets/images/17_gov3_bc_logo_transparent.svg"
                alt="B.C. Government Logo"
            />
        </a>
        <div class="content">
            <ul>
                <div v-for="item in props.data">
                    <li class="header">{{ item.name }}</li>
                    <ul>
                        <li
                            v-for="child in item.items"
                            class="child"
                            :class="{
                                'p-sidenav-selected':
                                    $router.currentRoute.value.path ==
                                    child.link,
                                'p-sidenav-disabled': child.disabled,
                            }"
                            @click="router.push(child.link)"
                        >
                            <Icon
                                class="p-sidenav-color-icon p-sidenav-padding-icon"
                                small
                                :icon="child.icon.toString()"
                            ></Icon>
                            {{ child.name }}
                        </li>
                    </ul>
                </div>
            </ul>
        </div>

        <div class="support-section p-sidenav-disabled">
            <ul>
                <li class="header">Support</li>
                <ul>
                    <li
                        class="child"
                        click="mailto:SIBIFSAF@Victoria1.gov.bc.ca"
                    >
                        <Icon
                            icon="HelpIcon"
                            small
                            class="p-sidenav-padding-icon"
                        />
                        Need help?
                    </li>
                </ul>
            </ul>
        </div>
    </nav>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
