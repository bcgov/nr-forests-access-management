<script setup lang="ts">
import { inject } from "vue";
import Button from "@/components/common/Button.vue";
import { IconSize } from "@/enum/IconEnum";
import { IdpProvider } from "@/enum/IdpEnum";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";

import logo from "@/assets/images/bc-gov-logo.png";
import TreeLogs from "@/assets/images/tree-logs.jpg";
import { AUTH_KEY } from "@/constants/InjectionKeys";
import type { IdpTypes, AuthContext } from "@/types/AuthTypes";

const environmentSettings = new EnvironmentSettings();
const isDevEnvironment = environmentSettings.isDevEnvironment();

const auth = inject<AuthContext>(AUTH_KEY);

const handleLogin = (idp: IdpTypes) => {
    if (auth) {
        auth.login(idp);
    } else {
        console.error("Auth context not found");
    }
};
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
                    @click="handleLogin(IdpProvider.IDIR)"
                >
                    <Icon icon="login" :size="IconSize.medium" />
                </Button>
                <Button
                    class="landing-button"
                    outlined
                    :disabled="!isDevEnvironment"
                    :label="`Login with ${IdpProvider.BCEIDBUSINESS}`"
                    id="login-business-bceid-button"
                    @click="handleLogin(IdpProvider.BCEIDBUSINESS)"
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
@import "@bcgov-nr/nr-theme/style-sheets/landing-page-components-overrides.scss";
</style>
