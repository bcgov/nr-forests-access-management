<script setup lang="ts">
import { useRouter } from "vue-router";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import PageTitle from "@/components/common/PageTitle.vue";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { Form } from "vee-validate";
import StepContainer from "@/components/UI/StepContainer.vue";
import { computed, ref, watch } from "vue";
import useAuth from "@/composables/useAuth";
import { UserType, type FamForestClientSchema } from "fam-app-acsctl-api/model";
import {
    getDefaultFormData,
    type AppPermissionFormType,
    getPageTitle,
    getRoleSectionTitle,
    getRoleSectionSubtitle,
    validateAppPermissionForm,
} from "@/views/AddAppPermission/utils";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import UserDomainSelect from "@/components/grantaccess/form/UserDomainSelect.vue";
import UserNameInput from "@/components/grantaccess/form/UserNameInput.vue";
import RoleSelectTable from "@/components/grantaccess/RoleSelectTable.vue";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import ForestClientSection from "@/components/grantaccess/ForestClientSection.vue";
import BoolCheckbox from "@/components/common/BoolCheckbox.vue";
import Button from "@/components/common/Button.vue";

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
});

const selectedApp = computed(() => {
    if (!adminUserAccessQuery.data.value) return null;

    return (
        adminUserAccessQuery.data.value.grants.find(
            (famGrantDetail) =>
                famGrantDetail.application.id === props.applicationId
        ) ?? null
    );
});

const formData = ref<AppPermissionFormType | undefined>(undefined);

watch(
    () => adminUserAccessQuery.isSuccess && selectedApp.value,
    (isSuccessful) => {
        if (isSuccessful) {
            formData.value = getDefaultFormData(
                auth.authState.famLoginUser?.idpProvider === "idir"
                    ? UserType.I
                    : UserType.B,
                env.isProdEnvironment() &&
                    selectedApp.value!.application.env === "PROD"
            );
        }
    },
    { immediate: true }
);

const handleDomainChange = (userType: UserType) => {
    if (formData.value) {
        formData.value.domain = userType;
        formData.value.userId = "";
        formData.value.userGuid = "";
    }
};

const handleUserIdChange = (userId: string) => {
    if (formData.value) {
        formData.value.userId = userId;
        formData.value.userGuid = "";
    }
};

const isUserIdVerified = ref(false);

const handleUserVerification = (
    isVerfied: boolean,
    userGuid: string = "",
    userEmail: string = ""
) => {
    if (formData.value) {
        isUserIdVerified.value = isVerfied;
        formData.value.userGuid = userGuid;
        formData.value.userEmail = userEmail;
    }
};

const isAbstractRoleSelected = (): boolean =>
    formData.value?.role?.type_code === "A";

const handleRoleChange = (role: FamRoleDto) => {
    if (formData.value) {
        formData.value.role = role;
    }
};

const clearForestClients = () => {
    if (formData.value) {
        formData.value.forestClients = [];
    }
};

const setVerifiedForestClients = (forestClients: FamForestClientSchema[]) => {
    if (formData.value) {
        formData.value.forestClients = forestClients;
    }
};

const onSubmit = () => {
    const plainObject = { ...formData.value };
    console.log("Form submitted with:", plainObject);
};
</script>

<template>
    <div class="add-app-permission-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            :title="getPageTitle(props.requestType)"
            :subtitle="`Adding user permission to ${selectedApp?.application.description}. All fields are mandatory`"
        />
        <div class="form-container">
            <Form
                v-slot="{ handleSubmit }"
                ref="form"
                as="div"
                v-if="formData"
                :validation-schema="
                    validateAppPermissionForm(isAbstractRoleSelected())
                "
                validate-on-submit
            >
                <form id="add-app-permission-form-id">
                    <StepContainer title="User information" divider>
                        <UserDomainSelect
                            class="domain-select"
                            v-if="
                                auth.authState.famLoginUser?.idpProvider ===
                                'idir'
                            "
                            :domain="formData.domain"
                            @change="handleDomainChange"
                        />
                        <UserNameInput
                            class="user-name-text-input"
                            :domain="formData.domain"
                            :userId="formData.userId"
                            :app-id="applicationId"
                            @change="handleUserIdChange"
                            @setVerifyResult="handleUserVerification"
                        />
                    </StepContainer>
                    <StepContainer
                        :title="getRoleSectionTitle(props.requestType)"
                        :subtitle="getRoleSectionSubtitle(props.requestType)"
                        divider
                        v-if="selectedApp?.roles"
                    >
                        <RoleSelectTable
                            :role="formData.role"
                            :roleOptions="selectedApp.roles"
                            @change="handleRoleChange"
                            @clearForestClients="clearForestClients"
                        />
                    </StepContainer>
                    <StepContainer
                        v-if="isAbstractRoleSelected()"
                        title="Organization information"
                        divider
                    >
                        <ForestClientSection
                            :userId="formData.userId"
                            :role="formData.role"
                            :app-id="props.applicationId"
                            :verified-clients="formData.forestClients"
                            @setVerifiedForestClients="setVerifiedForestClients"
                        />
                    </StepContainer>
                    <StepContainer :divider="false">
                        <BoolCheckbox
                            class="email-checkbox"
                            v-model="formData.sendUserEmail"
                            label="Send email to notify user"
                        />
                    </StepContainer>
                    <div class="button-group">
                        <Button label="Back" @click="" severity="secondary" />
                        <Button
                            label="Create Application Admin"
                            @click="handleSubmit(onSubmit)"
                            :icon="CheckmarkIcon"
                        />
                    </div>
                </form>
            </Form>
        </div>
    </div>
</template>
<style lang="scss">
.add-app-permission-container {
    padding-bottom: 2.5rem;
    .user-name-text-input {
        margin-top: 2rem;
    }
    .form-container {
        margin-top: 3rem;
        width: 60%; // Temporary until we implement the grid system
    }

    .domain-select {
        margin-top: 2.5rem;
    }

    .email-checkbox {
        margin-top: 2.5rem;
    }

    .button-group {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        margin-top: 3rem;
        .fam-button {
            width: 15.1875rem;
            height: 3rem;

            .button-label {
                @include type.type-style("body-compact-01");
            }
        }
    }
}
</style>
