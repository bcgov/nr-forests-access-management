<script setup lang="ts">
import TermsAndConditions from "@/components/common/TermsAndConditions.vue";
import Header from "@/components/UI/Header.vue";
import SideNav from "@/components/UI/SideNav.vue";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { useQuery } from "@tanstack/vue-query";

const termsAndConditionQuery = useQuery({
    queryKey: ["user_terms_conditions", "user:validate"],
    queryFn: () =>
        AppActlApiService.userTermsAndConditionsApi
            .validateUserRequiresAcceptTermsAndConditions()
            .then((res) => res.data),
});
</script>

<template>
    <div>
        <!-- Show layout and content -->
        <Header title="FAM" subtitle="Forests Access Management" />
        <SideNav />
        <div class="main">
            <main>
                <router-view />
            </main>
        </div>
    </div>
</template>
