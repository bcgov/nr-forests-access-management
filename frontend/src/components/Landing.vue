<script setup lang="ts">
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { IdpProvider } from '@/enum/IdpEnum';
import AuthService from '@/services/AuthService';
import logo from '@/assets/images/bc-gov-logo.png';
import TreeLogs from '@/assets/images/tree-logs.jpg';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';

const environmentSettings = new EnvironmentSettings();
const isDevEnvironment = environmentSettings.isDevEnvironment();
</script>

<template>
    <div class="full-width">
        <div class="row landing-grid">
            <div class="col-sm-6 col-md-7 col-lg-7">
                <img :src="logo" alt="BCGov Logo" width="160" class="logo" />
                <h1 id="landing-title" class="landing-title">Welcome to FAM</h1>
                <h2 id="landing-subtitle" class="landing-subtitle">
                    Forests Access Management
                </h2>

                <p id="landing-desc" class="landing-desc">
                    Grant access to your users
                </p>
                <Button
                    class="landing-button"
                    :label="`Login with ${IdpProvider.IDIR}`"
                    id="login-idir-button"
                    @click="AuthService.login()"
                >
                    <Icon icon="login" :size="IconSize.medium" />
                </Button>
                <Button
                    class="landing-button"
                    outlined
                    :disabled="!isDevEnvironment"
                    :label="`Login with ${IdpProvider.BCEIDBUSINESS}`"
                    id="login-business-bceid-button"
                    @click="AuthService.loginBusinessBceid()"
                >
                    <Icon icon="login" :size="IconSize.medium" />
                </Button>
            </div>
            <div class="col-sm-6 col-md-5 col-lg-5 landing-img-column">
                <img
                    :src="TreeLogs"
                    alt="Small green seedling on the dirt and watered"
                    class="landing-img"
                />
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@import '@bcgov-nr/nr-theme/style-sheets/landing-page-components-overrides.scss';
</style>
