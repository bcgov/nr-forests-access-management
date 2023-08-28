<script setup lang="ts">
import router from '@/router';
import type { PropType } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import { IconSize } from '@/enum/IconEnum';

export interface ISideNavData {
    name: string;
    items: [ISideNavItem];
}

export interface ISideNavItem {
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
    <nav class="sidenav">
        <a
            class="sidenav-logo"
            title="Forests Access Management"
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
                                'sidenav-selected':
                                    $router.currentRoute.value.path ==
                                    child.link,
                                'sidenav-disabled': child.disabled,
                            }"
                            @click="router.push(child.link)"
                        >
                            <Icon
                                class="custom-carbon-icon--sidenav"
                                :icon="child.icon.toString()"
                                :size="IconSize.small"
                            />
                            {{ child.name }}
                        </li>
                    </ul>
                </div>
            </ul>
        </div>

        <!-- Leaving this piece of code below commented out because we will need to reuse it again in the future when we have the functionality -->
        <!-- <div class="support-section sidenav-disabled">
            <ul>
                <li class="header">Support</li>
                <ul>
                    <li
                        class="child"
                        click="mailto:SIBIFSAF@Victoria1.gov.bc.ca"
                    >
                        <Icon
                            icon="help"
                            :size="IconSize.small"
                            class="custom-carbon-icon--help"
                        />
                        Need help?
                    </li>
                </ul>
            </ul>
        </div> -->
    </nav>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/default-theme.scss';
@import '@/assets/styles/styles.scss';

.sidenav-logo {
    img {
        margin: 0px 0px 16px 3px;
        width: 140px;
        height: 32px;
    }
}

.sidenav {
    position: fixed;
    padding: 16px 0px;
    width: 256px;
    height: calc(100vh - 50px);
    left: 0px;
    top: 48px;
    overflow-x: hidden;
    overflow-y: auto;
    box-shadow: inset -1px 0px 0px $light-border-subtle-00;
    .content {
        position: relative;
        min-height: auto;
    }
    .support-section {
        position: absolute;
        bottom: 0px;
    }
}

.sidenav ul {
    padding: 0;
    list-style-type: none;
}

.sidenav li.header {
    font-weight: 400;
}

.sidenav li {
    @extend %helper-text-01;
    color: $light-text-secondary;
    align-items: center;
    padding: 15px 16px;
    i {
        vertical-align: middle;
    }
    a {
        text-decoration: none;
    }
}

.sidenav li.child:hover {
    background: $light-layer-selected-01;
    box-shadow: inset 3px 0px 0px $light-border-interactive;
    color: $light-text-primary;
    cursor: pointer;
}

.sidenav-disabled {
    pointer-events: none;
    opacity: 0.6;
}

.sidenav-selected {
    background: $light-layer-selected-01;
    box-shadow: inset 3px 0px 0px $light-border-interactive;
    color: $light-text-primary !important;
    cursor: pointer;
}

.sidenav li a:hover,
ul#nav li.active a {
    color: $light-text-primary;
    background: $light-layer-selected-01;
    box-shadow: inset 3px 0px 0px $light-border-interactive;
}

.sidenav-padding-icon {
    margin-right: 25px;
}

.sidenav-color-icon {
    color: $light-interactive;
}
</style>
