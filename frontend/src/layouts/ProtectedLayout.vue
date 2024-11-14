<script setup lang="ts">
import { watch } from "vue";
import { isAxiosError } from "axios";
import { useRouter } from "vue-router";
import TermsAndConditions from "@/components/TermsAndConditions.vue";
import Header from "@/layouts/Header.vue";
import SideNav from "@/layouts/SideNav.vue";
import Spinner from "@/components/UI/Spinner.vue";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { showTermsForAcceptance } from "@/store/TermsAndConditionsState";
import { useQuery } from "@tanstack/vue-query";
import useAuth from "@/composables/useAuth";
import { NoAccessRoute } from "@/router/routes";

const auth = useAuth();
const router = useRouter();

/**
 * This request verifies whether the user needs to accept FAM's terms and conditions
 * before continuing in the app.
 *
 * Currently, if the user is a BCeID user and a delegated admin, they are required to accept
 * the terms and conditions.
 */
const termsAndConditionQuery = useQuery({
    queryKey: ["user_terms_conditions", "user:validate"],
    queryFn: () =>
        AppActlApiService.userTermsAndConditionsApi
            .validateUserRequiresAcceptTermsAndConditions()
            .then((res) => res.data),
});

watch(termsAndConditionQuery.status, () => {
    if (termsAndConditionQuery.status.value === "error") {
        const error = termsAndConditionQuery.error.value;
        if (isAxiosError(error)) {
            if (error.response?.status === 403) {
                router.push({ name: NoAccessRoute.name });
            } else {
                console.error("Error validating user permissions. ", error);
                auth.logout();
            }
        }
    }

    if (
        termsAndConditionQuery.status.value === "success" &&
        termsAndConditionQuery.data.value === true
    ) {
        showTermsForAcceptance();
    }
});
</script>

<template>
    <div>
        <!-- Show layout and content -->
        <TermsAndConditions />
        <Header title="FAM" subtitle="Forests Access Management" />
        <SideNav />
        <div class="main">
            <main>
                <div
                    v-if="termsAndConditionQuery.isLoading.value"
                    class="page-loading-spinner"
                >
                    <Spinner loading-text="Page loading" />
                </div>
                <router-view
                    v-if="termsAndConditionQuery.data.value === false"
                />
            </main>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.page-loading-spinner {
    display: flex;
    width: 100%;
    height: 80vh;
    justify-content: center;
    align-items: center;
}
</style>
