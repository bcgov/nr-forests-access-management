<script setup lang="ts">
import RoleSelectTable from "@/components/AddPermissions/RoleSelectTable.vue";
import UserDomainSelect from "@/components/AddPermissions/UserDomainSelect.vue";
import UserNameInput from "@/components/AddPermissions/UserNameSection.vue";
import BoolCheckbox from "@/components/UI/BoolCheckbox.vue";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import Button from "@/components/UI/Button.vue";
import PageTitle from "@/components/UI/PageTitle.vue";
import StepContainer from "@/components/UI/StepContainer.vue";
import useAuth from "@/composables/useAuth";
import { ManagePermissionsRoute } from "@/router/routes";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import {
    AddAppUserPermissionErrorQuerykey,
    AddAppUserPermissionSuccessQuerykey,
    AddDelegatedAdminErrorQuerykey,
    AddDelegatedAdminSuccessQuerykey,
    generatePayload,
    getRolesByAppId,
    getDefaultFormData,
    isAbstractRoleSelected,
    NewAppAdminQueryParamKey,
    NewDelegatedAddminQueryParamKey,
    validateAppPermissionForm,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import type { FamAccessControlPrivilegeCreateRequest } from "fam-admin-mgmt-api/model";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import {
    UserType,
    type FamUserRoleAssignmentCreateSchema,
    type IdimProxyBceidInfoSchema,
    type IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api/model";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";
import { Form } from "vee-validate";
import { computed, provide, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { isUserDelegatedAdminOnly } from "@/utils/AuthUtils";
import { IdpProvider } from "@/enum/IdpEnum";
import { activeTabIndex } from "@/store/ApplicationState";

const router = useRouter();
const auth = useAuth();
const environments = new EnvironmentSettings();

const props = defineProps<AddAppPermissionRouteProps>();

if (!props.appId) {
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
});

const rolesUnderSelectedApp = computed(() => {
    if (!adminUserAccessQuery.data.value) return null;

    const adminUserAccess = adminUserAccessQuery.data.value;

    const isDelegatedAdminOnly = isUserDelegatedAdminOnly(
        props.appId,
        adminUserAccess
    );

    const availableRoles = isDelegatedAdminOnly
        ? adminUserAccess.access.find(
              (authGrantDto) =>
                  authGrantDto.auth_key === AdminRoleAuthGroup.DelegatedAdmin
          )?.grants ?? []
        : adminUserAccess.access.find(
              (authGrantDto) =>
                  authGrantDto.auth_key === AdminRoleAuthGroup.AppAdmin
          )?.grants ?? [];

    return getRolesByAppId(availableRoles, props.appId);
});

const formData = ref<AppPermissionFormType | undefined>(undefined);

watch(
    () => adminUserAccessQuery.isSuccess && rolesUnderSelectedApp.value,
    (isSuccessful) => {
        if (isSuccessful) {
            formData.value = getDefaultFormData(
                auth.authState.famLoginUser?.idpProvider === "idir"
                    ? UserType.I
                    : UserType.B,
                environments.isProdEnvironment()
            );
        }
    },
    { immediate: true }
);

provide(APP_PERMISSION_FORM_KEY, formData);

const handleDomainChange = (userType: UserType) => {
    if (formData.value) {
        formData.value.domain = userType;
        formData.value.user = null;
    }
};

const handleUserVerification = (
    user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null,
    domain?: UserType
) => {
    if (formData.value) {
        formData.value.user = user;
        // Prevent user from chaning domain while it's verifying
        formData.value.domain = domain ?? formData.value.domain;
    }
};

const queryClient = useQueryClient();

const appAdminMutation = useMutation({
    mutationFn: (payload: FamUserRoleAssignmentCreateSchema) =>
        AppActlApiService.userRoleAssignmentApi.createUserRoleAssignmentMany(
            payload
        ),
    onSuccess: (res) => {
        queryClient.setQueryData(
            [AddAppUserPermissionSuccessQuerykey],
            res.data
        );
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.appId,
                [NewAppAdminQueryParamKey]: res.data.assignments_detail
                    .filter((assignment) => assignment.status_code === 200)
                    .map((assignment) => assignment.detail.user_role_xref_id)
                    .join(","),
            },
        });
    },
    onError: (error) => {
        queryClient.setQueryData([AddAppUserPermissionErrorQuerykey], {
            error,
            formData: formData.value,
        });
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.appId,
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
        queryClient.setQueryData([AddDelegatedAdminSuccessQuerykey], res.data);
        activeTabIndex.value = 1;
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.appId,
                [NewDelegatedAddminQueryParamKey]: res.data.assignments_detail
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
        queryClient.setQueryData([AddDelegatedAdminErrorQuerykey], {
            error,
            formData: formData.value,
        });
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.appId,
            },
        });
    },
    onSettled: () => {
        isSubmitting.value = false;
    },
    retry: 0,
});

const isSubmitting = ref<boolean>(false);
const isVerifyingUser = ref<boolean>(false);
const setIsVerifyingUser = (verifying: boolean) => {
    isVerifyingUser.value = verifying;
};

const confirm = useConfirm();

const onSubmit = () => {
    if (
        formData.value &&
        formData.value.forestClientInput.isValid &&
        !formData.value.forestClientInput.isVerifying
    ) {
        const payload = generatePayload(formData.value);
        if (!formData.value.isAddingDelegatedAdmin) {
            isSubmitting.value = true;
            appAdminMutation.mutate(payload);
        } else {
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

const getUserNameInputHelperText = () =>
    `Type user's ${
        formData.value?.domain === UserType.I
            ? IdpProvider.IDIR
            : IdpProvider.BCEIDBUSINESS
    } and click "Verify username"`;
</script>

<template>
    <div class="add-app-permission-container">
        <ConfirmDialog
            group="addDelegatedAdmin"
            class="confirm-dialog-with-blue-button"
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
            title="Add permission"
            :subtitle="`Add a new user permission to ${rolesUnderSelectedApp?.application.description}`"
        />
        <div class="app-permission-form-container container-fluid">
            <Form
                v-slot="{ handleSubmit }"
                ref="form"
                as="div"
                v-if="formData"
                :validation-schema="
                    validateAppPermissionForm(isAbstractRoleSelected(formData))
                "
                validate-on-submit
                class="row"
            >
                <form
                    id="add-app-permission-form-id"
                    class="col-sm-12 col-md-12 col-lg-10"
                >
                    <StepContainer title="User information" divider>
                        <UserDomainSelect
                            class="domain-select"
                            v-if="
                                auth.authState.famLoginUser?.idpProvider ===
                                'idir'
                            "
                            :domain="formData.domain"
                            :is-verifying-user="isVerifyingUser"
                            @change="handleDomainChange"
                        />
                        <UserNameInput
                            class="user-name-text-input"
                            :domain="formData.domain"
                            :user="formData.user"
                            :app-id="appId"
                            :helper-text="getUserNameInputHelperText()"
                            @setVerifyResult="handleUserVerification"
                            :set-is-verifying="setIsVerifyingUser"
                        />
                    </StepContainer>
                    <StepContainer
                        title="User roles"
                        subtitle="Select a role for this user"
                        divider
                        v-if="rolesUnderSelectedApp?.roles"
                    >
                        <RoleSelectTable
                            :app-id="appId"
                            :roleOptions="rolesUnderSelectedApp.roles"
                            :is-delegated-admin-only="
                                isUserDelegatedAdminOnly(
                                    props.appId,
                                    adminUserAccessQuery.data.value
                                )
                            "
                            role-field-id="role"
                            forest-clients-field-id="forestClients"
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
                                            appId: props.appId,
                                        },
                                    })
                            "
                        />
                        <Button
                            label="Add user permission"
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

    .app-permission-form-container {
        margin-top: 3rem;

        padding: 0;
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

            .p-progress-spinner-svg circle {
                stroke: colors.$white;
                animation: none;
            }
        }
    }
}
</style>
