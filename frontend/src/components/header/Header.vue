<script setup lang="ts">
import ProfileSidebar from '@/components/common/ProfileSidebar.vue';
import { useProfileSidebarVisible } from '@/store/ProfileVisibleState';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import authService from '@/services/AuthService';
import { IconSize } from '@/enum/IconEnum';

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
            class="navbar navbar-expand-md justify-content-between px-2 navbar-dark"
        >
            <span class="header-title">
                {{ props.title }}
                <strong>{{ props.subtitle }} {{ environmentLabel }}</strong>
            </span>

            <button
                class="navbar-toggler"
                type="button"
                title="Toggle Main Navigation"
                aria-controls="navbarNav"
                aria-expanded="false"
                aria-label="Toggle navigation"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
            >
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li>
                        <a
                            title="Log Out"
                            v-if="authService.getters.isLoggedIn()"
                            @click="useProfileSidebarVisible.toggleVisible()"
                        >
                            <Icon
                                icon="user--avatar"
                                :size=IconSize.medium
                            />
                        </a>
                    </li>
                </ul>
            </div>
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
