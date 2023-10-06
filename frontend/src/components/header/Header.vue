<script setup lang="ts">
import ProfileSidebar from '@/components/common/ProfileSidebar.vue';
import { IconSize } from '@/enum/IconEnum';
import authService from '@/services/AuthService';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { useProfileSidebarVisible } from '@/store/ProfileVisibleState';

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
            class="navbar justify-content-between flex-nowrap px-2"
        >
            <span class="header-title">
                {{ props.title }}
                <strong>{{ props.subtitle }} {{ environmentLabel }}</strong>
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
        a i {
            cursor: pointer;
        }
        margin: 0;
    }

    i {
        vertical-align: middle;
    }

    .navbar {
        margin: 0;
        padding: 0;
        height: 48px;
        vertical-align: middle;
    }

    .navbar-collapse {
        flex-grow: 0;
    }
}
</style>
