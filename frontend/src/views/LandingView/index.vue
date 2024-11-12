<script setup lang="ts">
import LoginIcon from "@carbon/icons-vue/es/login/16";
import Button from "primevue/button";
import { IdpProvider } from "@/enum/IdpEnum";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";

import logo from "@/assets/images/bc-gov-logo.png";
import TreeLogs from "@/assets/images/tree-logs.jpg";
import useAuth from "@/composables/useAuth";

const environmentSettings = new EnvironmentSettings();
const isDevEnvironment = environmentSettings.isDevEnvironment();

const auth = useAuth();
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

                <div class="landing-content">
                    <div class="button-group">
                        <v-slot />
                        <Button
                            class="landing-button"
                            :label="`Login with ${IdpProvider.IDIR}`"
                            id="login-idir-button"
                            @click="auth.login(IdpProvider.IDIR)"
                        >
                            <div class="button-content">
                                <span>
                                    {{ `Login with ${IdpProvider.IDIR}` }}
                                </span>
                                <LoginIcon />
                            </div>
                        </Button>

                        <Button
                            class="landing-button"
                            outlined
                            :disabled="!isDevEnvironment"
                            :label="`Login with ${IdpProvider.BCEIDBUSINESS}`"
                            id="login-business-bceid-button"
                            @click="auth.login(IdpProvider.BCEIDBUSINESS)"
                        >
                            <div class="button-content">
                                <span>
                                    {{
                                        `Login with ${IdpProvider.BCEIDBUSINESS}`
                                    }}
                                </span>
                                <LoginIcon />
                            </div>
                        </Button>
                    </div>
                </div>
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
.landing-img {
    width: 100%;
}
.landing-content {
    display: flex;
    flex-direction: column;
    .landing-button {
        .button-content {
            width: 100%;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
        }
    }
}
</style>
