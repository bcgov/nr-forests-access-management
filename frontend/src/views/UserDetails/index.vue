<script setup lang="ts">
import { useRoute } from "vue-router";
import { router } from "@/router";
import Button from "primevue/button";

import UserSummaryCard from "@/components/UserSummaryCard";
import PageTitle from "@/components/UI/PageTitle.vue";
import UserPermissionHistoryTable from "@/components/UserPermissionHistoryTable";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import { getApplicationById } from "@/utils/ApiUtils";

const route = useRoute();

// Access the path parameters
const userId = route.params.userId as string | undefined;
const applicationId = route.params.applicationId as string | undefined;

if (!userId || !applicationId) {
    console.warn("Missing required path params");
    router.push("/");
}

const navigateBack = () => {
    router.push({
        name: ManagePermissionsRoute.name,
        query: { appId: applicationId },
    });
};

/**
 * Get the FamApplicationDto with the applicationId,
 * it is used to display the app name in subtitle.
 */
const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => getApplicationById(Number(applicationId), data),
});

// Breadcrumb configuration
const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
    },
];
</script>

<template>
    <div class="user-detail-page-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            class="user-detail-page-title"
            title="Permissions History"
            :subtitle="`Check a user's ${adminUserAccessQuery.data.value?.description} permission history`"
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
