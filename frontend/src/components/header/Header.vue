<script setup lang="ts">
import authService from '@/services/AuthService';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { PrimeIcons } from 'primevue/api';

const environmentSettings = new EnvironmentSettings();
const environmentLabel = environmentSettings
    .getEnvironmentDisplayName('[', ']')
    .toUpperCase();
</script>

<template>
    <header class="app-header" id="header">
        <nav
            class="navbar navbar-expand-md justify-content-between px-2 navbar-dark"
        >
            <h2 class="title">
                Forest Access Management {{ environmentLabel }}
            </h2>

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
                    <li class="nav-item">
                        <a
                            class="nav-link nav-link-fade-up"
                            title="Log In"
                            v-if="!authService.getters.isLoggedIn()"
                            @click="authService.methods.login"
                        >
                            <span>Log In</span>
                        </a>
                    </li>
                    <li>
                        <a
                            title="Log Out"
                            v-if="authService.getters.isLoggedIn()"
                            @click="authService.methods.logout"
                        >
                            <i class="pi carbon-avatar-icon"></i>
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    </header>
</template>

<style lang="scss" scoped>
@import './header.scss';

.carbon-avatar-icon {
    height: 20px;
    width: 20px;

    -webkit-mask-image: url('@/assets/svg/user--avatar.svg');
    mask-image: url('@/assets/svg/user--avatar.svg');
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;

    background: currentColor;
}
</style>
