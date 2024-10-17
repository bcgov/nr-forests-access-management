<script setup lang="ts">
import { useRoute } from "vue-router";
import { router } from "@/router";
import Button from "primevue/button";
import UserSummaryCard from "@/components/UserSummaryCard";
import PageTitle from "@/components/common/PageTitle.vue";
import UserPermissionHistoryTable from "@/components/UserPermissionHistoryTable";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";

const route = useRoute();

// Access the path parameters
const userId = route.params.userId as string | undefined;
const applicationId = route.params.applicationId as string | undefined;

if (!userId || !applicationId) {
    console.warn("Missing required path params");
    router.push("/");
}

const navigateBack = () => {
    router.push("/");
};

// Breadcrumb configuration
const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        path: "/",
    },
];
</script>

<template>
    <div class="user-detail-page-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            class="user-detail-page-title"
            title="User Permissions History"
        />
        <UserSummaryCard :user-id="userId!" :application-id="applicationId!" />
        <div class="gray-container">
            <UserPermissionHistoryTable
                :user-id="userId!"
                :application-id="applicationId!"
            />
            <div class="back-button-container">
                <Button
                    label="Back"
                    severity="secondary"
                    @click="navigateBack"
                />
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.user-detail-page-container {
    display: flex;
    flex-direction: column;
    min-height: 93vh;

    .user-detail-page-title {
        margin-bottom: 2rem;
    }

    .gray-container {
        background-color: colors.$gray-10;
        flex-grow: 1;
        margin: 2.5rem -2.5rem 0 -2.5rem;
        padding: 2.5rem;

        .back-button-container {
            margin-top: 3rem;

            button {
                width: 15rem;

                .p-button-label {
                    @include type.type-style("body-compact-01");
                }
            }
        }
    }
}
</style>
