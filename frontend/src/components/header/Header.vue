<script setup lang="ts">
import Button from 'primevue/button';
import ProfileSidebar from '@/components/common/ProfileSidebar.vue';
import Icon from '@/components/common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';
import authService from '@/services/AuthService';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { profileSidebarState } from '@/store/ProfileSidebarState';
import { sideNavState } from '@/store/SideNavState';

const environmentSettings = new EnvironmentSettings();
const environmentLabel = environmentSettings
    .getEnvironmentDisplayName('[', ']')
    .toUpperCase();

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subtitle: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <header class="header" id="header">
        <nav class="navbar justify-content-start">
            <Button
                class="btn-toggle-sideNav"
                @click="sideNavState.toggleSideNavVisible()"
                aria-label="Toggle Side Navigation"
            >
                <Icon
                    class="custom-carbon-icon--menu"
                    icon="menu"
                    :size="IconSize.medium"
                />
            </Button>
            <span class="header-title">
                {{ props.title }}
                <strong class="subtitle"
                    >{{ props.subtitle }} {{ environmentLabel }}</strong
                >
            </span>

            <Button
                aria-label="open profile sidebar"
                :class="
                    `btn-toggle-profile
                    ${profileSidebarState.isVisible &&
                    'btn-toggle-profile-active'}`"
                title="Profile"
                v-if="authService.isLoggedIn()"
                @click="profileSidebarState.toggleVisible()"
            >
                <Icon

                    icon="user--avatar"
                    :size="IconSize.medium"
                />
            </Button>
        </nav>
        <teleport to=".modals">
            <ProfileSidebar />
        </teleport>
    </header>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/base.scss';

li {
    list-style: none;
}

.btn-toggle-sideNav {
    margin-right: 0.5rem;
    padding: 0.88rem;
    border: none;
    border-radius: 0;

    .label {
        display: none !important;
    }
}

.subtitle {
    display: none;
}

.header {
    @extend %heading-compact-01;
    position: fixed;

    font-size: 1rem;

    height: $header-height;
    width: $header-width;
    background: $light-background-brand;

    padding: 0;
    z-index: 1;
    color: $text-on-color;
    .header-title {
        margin: 0 auto 0 0;
    }

    i {
        vertical-align: middle;
    }

    .navbar {
        margin: 0;
        padding: 0 1px 0 1rem;
        height: 3rem;
        vertical-align: middle;
    }

    .navbar-collapse {
        flex-grow: 0;
    }
}

.btn-toggle-profile {
    border-radius: 0;
    border: none;
    padding-bottom: 0.93rem;

    svg {
        margin-top: 0.125rem;
    }
}

.btn-toggle-profile-active {
    color: #000;
    background-color: #fff;
}

.btn-toggle-profile:hover,
.btn-toggle-profile:focus  {
    color: #fff;
}

@media (min-width: 1024px) {

    .subtitle {
        display: inline;
    }

    .btn-toggle-sideNav {
        display: none;
    }
}
</style>
