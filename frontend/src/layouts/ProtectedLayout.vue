<script setup lang="ts">
import TermsAndConditions from "@/components/TermsAndConditions.vue";
import Header from "@/layouts/Header.vue";
import SideNav from "@/layouts/SideNav.vue";
import Spinner from "@/components/UI/Spinner.vue";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { showTermsForAcceptance } from "@/store/TermsAndConditionsState";
import { useQuery } from "@tanstack/vue-query";
import { watch } from "vue";

const termsAndConditionQuery = useQuery({
    queryKey: ["user_terms_conditions", "user:validate"],
    queryFn: () =>
        AppActlApiService.userTermsAndConditionsApi
            .validateUserRequiresAcceptTermsAndConditions()
            .then((res) => res.data),
});

watch(termsAndConditionQuery.isSuccess, () => {
    if (termsAndConditionQuery.data.value === true) {
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
