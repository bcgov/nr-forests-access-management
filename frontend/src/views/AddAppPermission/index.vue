<script setup lang="ts">
import { useRouter } from "vue-router";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import PageTitle from "@/components/common/PageTitle.vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { Form } from "vee-validate";
import StepContainer from "@/components/UI/StepContainer.vue";
import { computed, ref, watch } from "vue";
import useAuth from "@/composables/useAuth";
import {
    UserType,
    type FamForestClientSchema,
    type FamUserRoleAssignmentCreateSchema,
    type IdimProxyBceidInfoSchema,
    type IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api/model";
import {
    getDefaultFormData,
    type AppPermissionFormType,
    getPageTitle,
    getRoleSectionTitle,
    getRoleSectionSubtitle,
    validateAppPermissionForm,
    generatePayload,
    AppAdminSuccessQuerykey,
    AppAdminErrorQuerykey,
    DelegatedAdminSuccessQueryKey,
    DelegatedAdminErrorQueryKey,
    getApplicationWithUniqueRoles,
} from "@/views/AddAppPermission/utils";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import UserDomainSelect from "@/components/grantaccess/form/UserDomainSelect.vue";
import UserNameInput from "@/components/grantaccess/form/UserNameInput.vue";
import RoleSelectTable from "@/components/grantaccess/RoleSelectTable.vue";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import ForestClientSection from "@/components/grantaccess/ForestClientSection.vue";
import BoolCheckbox from "@/components/common/BoolCheckbox.vue";
import Button from "@/components/common/Button.vue";
import type { FamAccessControlPrivilegeCreateRequest } from "fam-admin-mgmt-api/model";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";

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
    select: (data) => {
        if (props.requestType === "addUserPermission") {
            const delegatedAdminGrants =
                data.access.find(
                    (authGrantDto) =>
                        authGrantDto.auth_key === "DELEGATED_ADMIN"
                )?.grants ?? [];
            const appAdminGrants =
                data.access.find(
                    (authGrantDto) => authGrantDto.auth_key === "APP_ADMIN"
                )?.grants ?? [];
            console.log(delegatedAdminGrants.concat(appAdminGrants));
            return delegatedAdminGrants.concat(appAdminGrants);
        } else {
            return (
                data.access.find(
                    (authGrantDto) => authGrantDto.auth_key === "APP_ADMIN"
                )?.grants ?? []
            );
        }
    },
});

const selectedApp = computed(() => {
    if (!adminUserAccessQuery.data.value) return null;

    // return (
    //     adminUserAccessQuery.data.value.find(
    //         (famGrantDetail) =>
    //             famGrantDetail.application.id === props.applicationId
    //     ) ?? null
    // );
    return getApplicationWithUniqueRoles(
        adminUserAccessQuery.data.value,
        props.applicationId
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
        formData.value.user = null;
    }
};

const handleUserVerification = (
    user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema,
    domain?: UserType
) => {
    if (formData.value) {
        formData.value.user = user;
        // Prevent user from chaning domain while it's verifying
        formData.value.domain = domain ?? formData.value.domain;
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

const queryClient = useQueryClient();

const appAdminMutation = useMutation({
    mutationFn: (payload: FamUserRoleAssignmentCreateSchema) =>
        AppActlApiService.userRoleAssignmentApi.createUserRoleAssignmentMany(
            payload
        ),
    onSuccess: (res) => {
        queryClient.setQueryData([AppAdminSuccessQuerykey], res.data);
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.applicationId,
                newAppAdminIds: res.data.assignments_detail
                    .filter((assignment) => assignment.status_code === 200)
                    .map((assignment) => assignment.detail.user_role_xref_id)
                    .join(","),
            },
        });
    },
    onError: (error) => {
        queryClient.setQueryData([AppAdminErrorQuerykey], {
            error,
            formData: formData.value,
        });
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.applicationId,
            },
        });
    },
    onSettled: () => {
        isSubmitting.value = false;
    },
    retry: 0,
});

const delegatedAdminMutation = useMutation({
    mutationFn: (payload: FamAccessControlPrivilegeCreateRequest) =>
        AdminMgmtApiService.delegatedAdminApi.createAccessControlPrivilegeMany(
            payload
        ),
    onSuccess: (res) => {
        queryClient.setQueryData([DelegatedAdminSuccessQueryKey], res.data);
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.applicationId,
                newDelegatedAdminIds: res.data.assignments_detail
                    .filter((assignment) => assignment.status_code === 200)
                    .map(
                        (assignment) =>
                            assignment.detail.access_control_privilege_id
                    )
                    .join(","),
            },
        });
    },
    onError: (error) => {
        queryClient.setQueryData([DelegatedAdminErrorQueryKey], {
            error,
            formData: formData.value,
        });
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.applicationId,
            },
        });
    },
    onSettled: () => {
        isSubmitting.value = false;
    },
    retry: 0,
});

const isSubmitting = ref<boolean>(false);

const confirm = useConfirm();

const onSubmit = () => {
    if (formData.value) {
        const payload = generatePayload(formData.value);

        if (props.requestType === "addUserPermission") {
            isSubmitting.value = true;
            appAdminMutation.mutate(payload);
        } else if (props.requestType === "addDelegatedAdmin") {
            confirm.require({
                group: "addDelegatedAdmin",
                header: "Add a delegated admin",
                rejectLabel: "Cancel",
                acceptLabel: "Submit delegated admin",
                acceptClass: "dialog-accept-button",
                accept: () => {
                    isSubmitting.value = true;
                    delegatedAdminMutation.mutate(payload);
                },
            });
        }
    }
};
</script>

<template>
    <div class="add-app-permission-container">
        <ConfirmDialog
            group="addDelegatedAdmin"
            class="delegated-admin-confrim-dialog"
        >
            <template #message>
                <p>
                    Are you sure you want to add
                    <strong>{{ formData?.user?.userId.toUpperCase() }}</strong>
                    as a delegated admin? As a delegated admin
                    <strong>{{ formData?.user?.userId.toUpperCase() }}</strong>
                    will be able to add, edit or delete users
                </p>
            </template>
        </ConfirmDialog>
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
                            :user="formData.user"
                            :app-id="applicationId"
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
                        <Button
                            label="Back"
                            severity="secondary"
                            @click="
                                () =>
                                    router.push({
                                        name: ManagePermissionsRoute.name,
                                        query: {
                                            appId: props.applicationId,
                                        },
                                    })
                            "
                        />
                        <Button
                            :label="`Create ${
                                props.requestType === 'addUserPermission'
                                    ? 'Application'
                                    : 'Delegated'
                            } Admin`"
                            @click="handleSubmit(onSubmit)"
                            :icon="CheckmarkIcon"
                            :is-loading="isSubmitting"
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

.delegated-admin-confrim-dialog {
    .p-confirm-dialog-accept {
        border: 0.0625rem solid colors.$blue-60;
        background-color: colors.$blue-60;
    }

    .dialog-accept-button:hover {
        border: 0.0625rem solid colors.$blue-65;
        background-color: colors.$blue-65;
    }
}
</style>
