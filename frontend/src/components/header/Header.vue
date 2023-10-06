<script setup lang="ts">
import ProfileSidebar from '@/components/common/ProfileSidebar.vue';
import Button from 'primevue/button';
import Icon from '@/components/common/Icon.vue';
import { IconSize } from '@/enum/IconEnum';
import authService from '@/services/AuthService';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { useProfileSidebarVisible } from '@/store/ProfileVisibleState';
import { useSideNavVisible } from '@/store/SideNavState'

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
        <nav
            class="navbar justify-content-start"
        >
            <Button
                class="btn-toggleSideNav"
                @click="useSideNavVisible.toggleSideNavVisible()"
            >
                <Icon
                    class="custom-carbon-icon--menu"
                    icon="menu"
                    :size="IconSize.medium"
                />
            </Button>
            <span class="header-title">
                {{ props.title }}
                <strong class="subtitle">{{ props.subtitle }} {{ environmentLabel }}</strong>
            </span>

                <a
                    title="Profile"
                    v-if="authService.getters.isLoggedIn()"
                    @click="useProfileSidebarVisible.toggleVisible()"
                >
                    <Icon icon="user--avatar" :size="IconSize.medium" />
                </a>

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

.btn-toggleSideNav {
    margin-right: 0.5rem;
    padding: 0.88rem;
    border: none;
    border-radius: 0;
}
.subtitle {
    display: none
}
.header {
    @extend %heading-compact-01;
    position: fixed;

    height: $header-height;
    width: $header-width;
    background: $light-background-brand;

    padding: 0;
    z-index: 1;
    color: $dark-text-primary;
    .header-title {
        margin: 0 auto 0 0 ;
        a i {
            cursor: pointer;
        }
    }

    i {
        vertical-align: middle;
    }

    .navbar {
        margin: 0;
        padding: 0 1rem 0 0;
        height: 3rem;
        vertical-align: middle;
    }

    .navbar-collapse {
        flex-grow: 0;
    }
}

@media (min-device-width: 1024px) {
    .navbar {
        padding: 0 1rem 0 1rem  !important;
    }
    .btn-toggleSideNav {
        display: none;
    }
}
</style>
