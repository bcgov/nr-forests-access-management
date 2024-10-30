<script setup lang="ts">
import { useRouter } from "vue-router";

import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import PageTitle from "@/components/common/PageTitle.vue";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { ErrorMessage, Field, Form } from "vee-validate";
import StepContainer from "@/components/UI/StepContainer.vue";
import { computed, ref, watch } from "vue";
import useAuth from "@/composables/useAuth";
import { UserType } from "fam-app-acsctl-api/model";
import { getDefaultFormData, type AppPermissionFormType } from "./utils";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";

const router = useRouter();
const auth = useAuth();
const env = new EnvironmentSettings();

const props = defineProps<AddAppPermissionRouteProps>();

if (
    !props.applicationId ||
    !props.requestType ||
    (props.requestType !== "addUserPermission" &&
        props.requestType !== "addDelegatedAdmin")
) {
    console.warn("Invalid or missing required query params");
    router.push("/");
}

const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
    },
];

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) =>
        props.requestType === "addUserPermission"
            ? data.access.find(
                  (authGrantDto) => authGrantDto.auth_key === "APP_ADMIN"
              )
            : data.access.find(
                  (authGrantDto) => authGrantDto.auth_key === "DELEGATED_ADMIN"
              ),
    refetchOnMount: "always",
});

const getPageTitle = (): string =>
    props.requestType === "addUserPermission"
        ? "Add user permission"
        : "Add a delegated admin";

const formData = ref<AppPermissionFormType>();

const selectedApp = computed(() => {
    if (!adminUserAccessQuery.data.value) return null;

    return (
        adminUserAccessQuery.data.value.grants.find(
            (famGrantDetail) =>
                famGrantDetail.application.id === props.applicationId
        ) ?? null
    );
});

watch(
    () => adminUserAccessQuery.isSuccess,
    (isSuccessful) => {
        if (isSuccessful && selectedApp.value) {
            formData.value = getDefaultFormData(
                auth.authState.famLoginUser?.idpProvider === "IDIR"
                    ? UserType.I
                    : UserType.B,
                env.isProdEnvironment() &&
                    selectedApp.value.application.env === "PROD"
            );
        }
    },
    { immediate: true }
);
</script>

<template>
    <div class="add-app-permission-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            :title="getPageTitle()"
            :subtitle="`Adding user permission to ${selectedApp?.application.description}. All fields are mandatory`"
        />
        <div class="form-container">
            <StepContainer title="User information" divider>
                <Form ref="form" v-slot="{ meta }" as="div"> </Form>
            </StepContainer>
        </div>
    </div>
</template>
<style lang="scss">
.add-app-permission-container {
    .form-container {
        margin-top: 3rem;
        width: 65%;
    }
}
</style>
