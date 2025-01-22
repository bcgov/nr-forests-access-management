<script setup lang="ts">
import { isAxiosError } from "axios";
import { useQuery } from "@tanstack/vue-query";
import Card from "primevue/card";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { DEFAULT_COL_SIZE } from "@/components/UserSummaryCard/constants";
import CardColumn from "@/components/CardColumn/index.vue";
import { formatFullName } from "@/utils/UserUtils";

const props = defineProps<{
    userId: string; // Fam User ID
    appId: string;
}>();

const userQuery = useQuery({
    queryKey: ["fam_applications", props.appId, "users", props.userId],
    queryFn: () =>
        AppActlApiService.applicationsApi
            .getApplicationUserById(Number(props.userId), Number(props.appId))
            .then((res) => res.data),
    enabled: !!props.userId && !!props.appId,
});
</script>

<template>
    <Card class="user-summary-card">
        <template #title> User Summary </template>
        <template #content v-if="userQuery.isError.value">
            Failed to fetch user info error.
            {{
                isAxiosError(userQuery.error.value)
                    ? `${userQuery.error.value.status} ${userQuery.error.value.message}`
                    : null
            }}
        </template>
        <template #content v-else>
            <div class="row gy-4">
                <CardColumn
                    :class="DEFAULT_COL_SIZE"
                    id="user-name"
                    label="Username"
                    :description="userQuery.data.value?.user_name"
                    :is-loading="userQuery.isFetching.value"
                />

                <CardColumn
                    :class="DEFAULT_COL_SIZE"
                    id="full-name"
                    label="Full name"
                    :description="
                        formatFullName(
                            userQuery.data.value?.first_name,
                            userQuery.data.value?.last_name
                        )
                    "
                    :is-loading="userQuery.isFetching.value"
                />

                <CardColumn
                    :class="DEFAULT_COL_SIZE"
                    id="domain"
                    label="Domain"
                    :description="userQuery.data.value?.user_type.description"
                    :is-loading="userQuery.isFetching.value"
                />

                <CardColumn
                    :class="DEFAULT_COL_SIZE"
                    id="email"
                    label="Email"
                    :description="userQuery.data.value?.email"
                    :is-loading="userQuery.isFetching.value"
                />
            </div>
        </template>
    </Card>
</template>

<style lang="scss">
.user-summary-card {
    border-radius: 0.5rem;

    .p-card-body {
        padding: 2rem;
    }

    .p-card-title {
        font-size: 1.25rem;
    }

    .p-card-content {
        padding-bottom: 0;
    }
}
</style>
