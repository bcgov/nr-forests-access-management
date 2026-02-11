<script setup lang="ts">
import RoleSelectTable from "@/components/AddPermissions/RoleSelectTable.vue";
import UserDomainSelect from "@/components/AddPermissions/UserDomainSelect.vue";
import UserNameInput from "@/components/AddPermissions/UserNameSection.vue";
import DatePicker from "@/components/DatePicker.vue";
import BoolCheckbox from "@/components/UI/BoolCheckbox.vue";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import Button from "@/components/UI/Button.vue";
import PageTitle from "@/components/UI/PageTitle.vue";
import StepContainer from "@/components/UI/StepContainer.vue";
import useAuth from "@/composables/useAuth";
import {
    ADD_PERMISSION_SELECT_USER_KEY,
    useSelectUserManagement,
} from "@/composables/useSelectUserManagement";
import { ManagePermissionsRoute } from "@/router/routes";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { activeTabIndex } from "@/store/ApplicationState";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import { isUserDelegatedAdminOnly } from "@/utils/AuthUtils";
import { currentDateInBCTimezone } from "@/utils/DateUtils";
import {
    AddAppUserPermissionErrorQuerykey,
    AddAppUserPermissionSuccessQuerykey,
    AddDelegatedAdminErrorQuerykey,
    AddDelegatedAdminSuccessQuerykey,
    generatePayload,
    getDefaultFormData,
    getRolesByAppId,
    getUserNameInputHelperText,
    NewDelegatedAddminQueryParamKey,
    NewRegularUserQueryParamKey,
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
} from "fam-app-acsctl-api/model";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";
import { useForm } from "vee-validate";
import { computed, provide, ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const auth = useAuth();
const environments = new EnvironmentSettings();

const props = defineProps<AddAppPermissionRouteProps>();

if (!props.appId) {
    console.warn("Invalid or missing required query params");
    router.push("/");
}

const hasSubmitted = ref(false);
const userErrorMessage = computed(() => (hasSubmitted.value ? errors.value.users ?? "" : ""));

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

const {
    handleSubmit,
    errors,
    values,
    setFieldValue,
    meta,
    setValues,
} = useForm<AppPermissionFormType>({
    validationSchema: validateAppPermissionForm(),
    initialValues: getDefaultFormData(
        auth.authState.famLoginUser?.idpProvider === "idir"
            ? UserType.I
            : UserType.B,
        environments.isProdEnvironment()
    ),
});

// Select user  management
// single-user select for delegated admin or multi-users select for regular users
const selectUserManagement = useSelectUserManagement(true); // Initially multi-user mode
provide(ADD_PERMISSION_SELECT_USER_KEY, selectUserManagement);

watch(
    () => adminUserAccessQuery.isSuccess && rolesUnderSelectedApp.value,
    (isSuccessful) => {
        if (isSuccessful) {
            setValues(
                getDefaultFormData(
                auth.authState.famLoginUser?.idpProvider === "idir"
                    ? UserType.I
                    : UserType.B,
                environments.isProdEnvironment()
            ));
        }
    },
    { immediate: true }
);

/**
 * Performs the actual domain change and clears user list.
 */
const performDomainChange = (userType: UserType) => {
    setFieldValue("domain", userType);
    setFieldValue("users", []);
    // Clear composable user lists on domain change
    selectUserManagement.clearUsers();
};

/**
 * Handles domain change from UserDomainSelect.
 * Shows confirmation dialog if selected user list is not empty.
 */
const handleDomainChange = (userType: UserType) => {
    if (selectUserManagement.userList.value.length > 0) {
        confirm.require({
            group: "changeDomain",
            header: "Changing User Domain",
            rejectLabel: "Cancel",
            acceptLabel: "Continue",
            acceptClass: "dialog-accept-button",
            accept: () => performDomainChange(userType),
        });
    } else {
        performDomainChange(userType);
    }
};

watch(
    () => selectUserManagement.userList.value,
    (newUsers) => {
        if (newUsers.length || meta.value.dirty) {
            setFieldValue("users", Array.from(newUsers));
        }
    },
    { deep: true }
);

watch(
    () => values.isAddingDelegatedAdmin,
    (isDelegatedAdmin) => {
        // Update composable mode based on form state
        selectUserManagement.multiUserMode = !isDelegatedAdmin;
    }
);

const queryClient = useQueryClient();

const assignUserRoles = useMutation({
    mutationFn: (payload: FamUserRoleAssignmentCreateSchema) =>
        AppActlApiService.userRoleAssignmentApi.createUserRoleAssignmentMany(
            payload
        ),
    onSuccess: (res) => {
        queryClient.setQueryData(
            [AddAppUserPermissionSuccessQuerykey],
            res.data
        );
        activeTabIndex.value = 0;
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: props.appId,
                [NewRegularUserQueryParamKey]: res.data.assignments_detail
                    .filter((assignment) => assignment.status_code === 200)
                    .map((assignment) => assignment.detail!.user_role_xref_id)
                    .join(","),
            },
        });
    },
    onError: (error) => {
        queryClient.setQueryData([AddAppUserPermissionErrorQuerykey], {
            error,
            formData: values,
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
            formData: values,
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
    hasSubmitted.value = true;
    if (
        values &&
        values.forestClientInput.isValid &&
        !values.forestClientInput.isVerifying
    ) {
        const payload = generatePayload(values);
        if (!values.isAddingDelegatedAdmin) {
            isSubmitting.value = true;
            assignUserRoles.mutate(payload as FamUserRoleAssignmentCreateSchema);
        } else {
            confirm.require({
                group: "addDelegatedAdmin",
                header: "Add a delegated admin",
                rejectLabel: "Cancel",
                acceptLabel: "Submit delegated admin",
                acceptClass: "dialog-accept-button",
                accept: () => {
                    isSubmitting.value = true;
                    delegatedAdminMutation.mutate(payload as FamAccessControlPrivilegeCreateRequest);
                },
            });
        }
    }
};

const onInvalid = () => {
    hasSubmitted.value = true;
};

</script>

<template>
    <div class="add-app-permission-container">
        <ConfirmDialog
            group="changeDomain"
            class="confirm-dialog-with-blue-button"
        >
            <template #message>
                <p>
                    Changing the domain will remove the user{{
                        selectUserManagement.userList.value.length > 1 ? "s" : ""
                    }} you've added. Are you sure you want to continue?
                </p>
            </template>
        </ConfirmDialog>
        <ConfirmDialog
            group="addDelegatedAdmin"
            class="confirm-dialog-with-blue-button"
        >
            <template #message>
                <p>
                    Are you sure you want to add
                    <strong>{{ values?.users?.[0]?.userId.toUpperCase() }}</strong>
                    as a delegated admin? As a delegated admin
                    <strong>{{ values?.users?.[0]?.userId.toUpperCase() }}</strong>
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
            <form
                id="add-app-permission-form-id"
                class="col-sm-12 col-md-12 col-lg-10 row"
                @submit.prevent="handleSubmit(onSubmit, onInvalid)()"
            >
                    <StepContainer title="User information" divider>
                        <UserDomainSelect
                            class="domain-select"
                            v-if="auth.authState.famLoginUser?.idpProvider === 'idir'"
                            :domain="values.domain"
                            :is-verifying-user="isVerifyingUser"
                            @domain-change-request="handleDomainChange"
                        />
                        <UserNameInput
                            class="user-name-text-input"
                            :domain="values.domain"
                            :app-id="appId"
                            :helper-text="getUserNameInputHelperText(values.domain)"
                            :set-is-verifying="setIsVerifyingUser"
                            :injection-key="ADD_PERMISSION_SELECT_USER_KEY"
                            :error-message="userErrorMessage"
                        />
                    </StepContainer>
                    <StepContainer
                        title="User roles"
                        subtitle="Select a role for this user"
                        divider
                        v-if="rolesUnderSelectedApp?.roles"
                    >
                        <!--
                          Use an arrow function to cast 'field' to 'any' before passing to setFieldValue.
                          This ensures type compatibility between the child and vee-validate's setFieldValue,
                          which may expect a more specific field type. The cast avoids TypeScript errors when
                          the child passes arbitrary field names.
                          [TODO]: In future, should redesign child component to not be tightly coupled with
                                  parent's form manipulation logic within child component.
                        -->
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
                            :set-field-value="(field: string, value: any) => setFieldValue(field as any, value)"
                            :formValues="values"
                        />
                    </StepContainer>
                    <StepContainer
                        title="User expiry date"
                        divider
                        v-if="!values?.isAddingDelegatedAdmin"
                    >
                        <DatePicker
                            :modelValue="values.expiryDate"
                            @update:datePickerValue="setFieldValue('expiryDate', $event)"
                            title="Expiry date (optional)"
                            description="By default, this role does not expire. Set an expiry date if you want the permission to end automatically."
                            :minDate="currentDateInBCTimezone()"
                        />
                    </StepContainer>
                    <StepContainer :divider="false">
                        <BoolCheckbox
                            class="email-checkbox"
                            :model-value="values.sendUserEmail"
                            @update:model-value="(val) => setFieldValue('sendUserEmail', val)"
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
                            type="submit"
                            :icon="CheckmarkIcon"
                            :is-loading="isSubmitting"
                        />
                    </div>
            </form>
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
