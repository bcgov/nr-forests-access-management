<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Auth } from "aws-amplify";
import type { ISideNavItem } from "@/components/common/SideNav.vue";
import Header from "@/components/header/Header.vue";
import SideNav from "@/components/common/SideNav.vue";
import sideNavData from "@/static/sideNav.json";

// State for side navigation data
const navigationData = ref<[ISideNavItem]>(sideNavData as any);

// Router instance
const router = useRouter();

// State for user authentication
const isAuthenticated = ref(false);

// Check if the user is authenticated via AWS Amplify's Auth module
const checkAuthentication = async () => {
    try {
        // This will throw an error if the user is not authenticated
        await Auth.currentAuthenticatedUser();
        isAuthenticated.value = true; // Set as authenticated if user exists
    } catch (error) {
        console.log("User is not authenticated, redirecting to landing page");
        isAuthenticated.value = false;
        router.push("/"); // Redirect to landing page
    }
};

// Run authentication check when the component is mounted
onMounted(() => {
    checkAuthentication();
});
</script>

<template>
    <div v-if="isAuthenticated">
        <!-- Show layout and content only if authenticated -->
        <Header title="FAM" subtitle="Forests Access Management" />
        <SideNav :data="navigationData" />
        <div class="main">
            <main>
                <RouterView />
                <!-- Render protected routes here -->
            </main>
        </div>
    </div>

    <div v-else>
        <!-- Show a message or loader while redirecting -->
        <p>Redirecting to landing page...</p>
    </div>
</template>
