<script setup lang="ts">
import Button from '@/components/common/Button.vue';
import authService from '@/services/AuthService';
import logo from '../assets/images/bc-gov-logo.png';
import TreeLogs from '../assets/images/tree-logs.jpg';
import { IconSize } from '@/enum/IconEnum';
</script>

<template>
    <div class="full-width">
        <div class="row landing-grid">
            <div class="col-sm-6 col-md-7 col-lg-7">
                <img :src="logo" alt="BCGov Logo" width="160" class="logo" />
                <h1 id="landing-title" class="landing-title">Welcome to FAM</h1>
                <h2 id="landing-subtitle" class="landing-subtitle">
                    Forestry Access Management
                </h2>

                <p id="landing-desc" class="landing-desc">
                    Grant access to your users
                </p>
                <Button
                    class="landing-button p-button-primary"
                    label="Login with IDIR"
                    @click="authService.methods.login"
                >
                    <Icon
                        icon="login"
                        :size="IconSize.medium"
                    />
                </Button>
                <Button
                    class="landing-button p-button-outlined"
                    label="Login with BCeID"
                    disabled
                    @click="authService.methods.login"
                >
                    <Icon
                        icon="login"
                        :size=IconSize.medium
                    />
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
@import '@bcgov-nr/nr-fsa-theme/style-sheets/landing-page-components-overrides.scss';
</style>
