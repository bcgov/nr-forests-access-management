<template>
    <nav class="sidenav">
        <a
            class="navbar-brand"
            title="Forest Access Management"
            href="https://www2.gov.bc.ca"
            style="margin-right: 3px"
        >
            <img
                class="nav-logo"
                src="@/assets/images/17_gov3_bc_logo_transparent.svg"
                alt="B.C. Government Logo"
            />
        </a>
        <div class="content">
            <ul style="position: relative">
                <div v-for="item in listItems">
                    <li class="header">{{ item.name }}</li>
                    <ul>
                        <li
                            v-for="child in item.items"
                            class="child"
                            :class="{
                                selected:
                                    $router.currentRoute.value.path ==
                                    child.link,
                                disabled: child.disabled,
                            }"
                            @click="router.push(child.link)"
                        >
                            <Icon
                                class="color-icon padding-icon"
                                small
                                :icon="child.icon.toString()"
                            ></Icon>
                            {{ child.name }}
                        </li>
                    </ul>
                </div>
            </ul>
        </div>

        <div class="support-section disabled">
            <ul>
                <li class="header">Support</li>
                <ul>
                    <li
                        class="child"
                        click="mailto:SIBIFSAF@Victoria1.gov.bc.ca"
                    >
                        <Icon icon="Help" small class="padding-icon" />
                        Need help?
                    </li>
                </ul>
            </ul>
        </div>
    </nav>
</template>

<script setup lang="ts">
import router from '@/router';
import { onMounted, ref, type PropType, defineAsyncComponent } from 'vue';
import type { RouteLocationRaw } from 'vue-router';

interface ISideBarData {
    name: String;
    items: [ISideBarItem];
}

interface ISideBarItem {
    name: String;
    icon: String;
    link: RouteLocationRaw;
    disabled: boolean;
}

const props = defineProps({
    data: {
        type: Object as PropType<ISideBarData[]>,
        required: true,
        default: '',
    },
});

const listItems = ref<ISideBarData[]>([]);

onMounted(() => {
    listItems.value = props.data;
});
</script>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.nav-logo {
    padding: 0px 16px;
    width: 140px;
    height: 32px;
}
.sidenav {
    /* UI shell - Left panel */

    /* Auto layout */
    position: fixed;
    padding: 16px 0px;
    overflow-y: auto;

    width: 256px;
    height: calc(100vh - 50px);
    left: 0px;
    top: $header-height;
    overflow-x: hidden;
    overflow-y: auto;

    background: #ffffff;
    box-shadow: inset -1px 0px 0px #dfdfe1;

    .content {
        min-height: auto;
    }

    .support-section {
        position: absolute;
        bottom: 0px;
        color: rgba(19, 19, 21, 0.25);
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
    /* Utility styles/helper-text-01 */
    font-family: 'BC Sans';
    font-style: normal;
    font-weight: 700;
    font-size: 12px;
    line-height: 48px;
    /* or 133% */
    letter-spacing: 0.32px;

    /* Light Theme/Text/$text-secondary */
    color: #606062;

    align-items: center;
    padding-left: 16px;

    height: 48px;
    i {
        vertical-align: middle;
    }

    a {
        text-decoration: none;
    }
}

.sidenav li.child:hover {
    background: rgba(147, 147, 149, 0.2);
    /* Light Theme/$border-interactive - Inner/Border left */
    box-shadow: inset 3px 0px 0px #0073e6;
    color: inherit;
    cursor: pointer;
}

.disabled {
    pointer-events: none; //This makes it not clickable
    opacity: 0.6; //This grays it out to look disabled
}

.selected {
    background: rgba(147, 147, 149, 0.2);
    /* Light Theme/$border-interactive - Inner/Border left */
    box-shadow: inset 3px 0px 0px #0073e6;
    color: inherit;
    cursor: pointer;
}

.sidenav li a:hover,
ul#nav li.active a {
    // here styling
    color: #131315;
    background: rgba(147, 147, 149, 0.2);
    /* Light Theme/$border-interactive - Inner/Border left */
    box-shadow: inset 3px 0px 0px #0073e6;
}

.carbon-dashboard-icon {
    height: 16px;
    width: 16px;

    -webkit-mask-image: url('@/assets/svg/dashboard.svg');
    mask-image: url('@/assets/svg/dashboard.svg');
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;

    background: #0073e6;

    margin-right: 25px;
}

.carbon-virtual-column--key-icon {
    height: 16px;
    width: 16px;

    -webkit-mask-image: url('@/assets/svg/virtual-column--key.svg');
    mask-image: url('@/assets/svg/virtual-column--key.svg');
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;

    background: #0073e6;

    margin-right: 25px;
}

.carbon-settings-icon {
    height: 16px;
    width: 16px;

    -webkit-mask-image: url('@/assets/svg/settings.svg');
    mask-image: url('@/assets/svg/settings.svg');
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;

    background: #0073e6;

    margin-right: 25px;
}

.padding-icon {
    margin-right: 25px;
}

.color-icon {
    color: #0073e6;
}
</style>
