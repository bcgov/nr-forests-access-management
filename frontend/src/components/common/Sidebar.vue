<template>
    <div class="sidenav">
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
        <ul>
            <li class="header">Main activities</li>
            <ul>
                <li class="child" @click="router.push('/dashboard')">
                    <i class="pi carbon-dashboard-icon"></i>Dashboard
                </li>
                <li class="child" @click="router.push('/application')">
                    <i class="pi carbon-virtual-column--key-icon"></i>Grant
                    Access
                </li>
            </ul>
            <li class="header">Management</li>
            <ul>
                <li class="child">
                    <i class="pi carbon-settings-icon"></i>Settings
                </li>
            </ul>
        </ul>

        <div class="support-section">
            <ul>
                <li class="header">Support</li>
                <ul>
                    <li class="child">
                        <i class="pi carbon-help-icon"></i>Need help?
                    </li>
                </ul>
            </ul>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import router from '@/router';

const selected = ref('');
const props = defineProps({
    visibleRight: {
        type: Boolean,
        required: true,
        default: {
            visibleRight: false,
        },
    },
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
    z-index: 1;
    padding: 16px 0px;
    // gap: 8px;

    width: 256px;
    height: calc(100vh - 50px);
    left: 0px;
    top: 48px;
    overflow-x: hidden;
    // padding-top: 20px;

    background: #ffffff;
    box-shadow: inset -1px 0px 0px #dfdfe1;
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
    // padding: 15px 16px;
    padding-left: 16px;
    // gap: 24px;

    height: 48px;
    i {
        vertical-align: middle;
    }
}

.sidenav li.child:hover {
    background: rgba(147, 147, 149, 0.2);
    /* Light Theme/$border-interactive - Inner/Border left */
    box-shadow: inset 3px 0px 0px #0073e6;
    color: inherit;
    cursor: pointer;
}

.support-section {
    margin-top: auto;
    position: absolute;
    bottom: 0px;
    color: rgba(19, 19, 21, 0.25);
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

.carbon-help-icon {
    height: 16px;
    width: 16px;

    -webkit-mask-image: url('@/assets/svg/help.svg');
    mask-image: url('@/assets/svg/help.svg');
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;

    background: currentColor;

    margin-right: 25px;
}
</style>
