<script setup lang="ts">
import RoleSelectTable from "@/components/AddPermissions/RoleSelectTable.vue";
import DatePicker from "@/components/DatePicker.vue";
import UserSearch from "@/components/Search/UserSearch.vue";
import BoolCheckbox from "@/components/UI/BoolCheckbox.vue";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import Button from "@/components/UI/Button.vue";
import PageTitle from "@/components/UI/PageTitle.vue";
import StepContainer from "@/components/UI/StepContainer.vue";
import useAuth from "@/composables/useAuth";
import { FAM_APPLICATION_NAME } from "@/constants/constants";
import { ManagePermissionsRoute } from "@/router/routes";
import {
    AdminMgmtApiService,
    AppActlApiService,
} from "@/services/ApiServiceFactory";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { activeTabIndex } from "@/store/ApplicationState";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";
import type { SelectedUser } from "@/types/SelectUserType";
import { isUserDelegatedAdminOnly } from "@/utils/AuthUtils";
import { currentDateInBCTimezone } from "@/utils/DateUtils";
import { scrollToRef } from "@/utils/WindowUtils";
import {
    AddAppUserPermissionErrorQuerykey,
    AddAppUserPermissionSuccessQuerykey,
    AddDelegatedAdminErrorQuerykey,
    AddDelegatedAdminSuccessQuerykey,
    generatePayload,
    getDefaultFormData,
    getRolesByAppId,
    NewDelegatedAddminQueryParamKey,
    NewRegularUserQueryParamKey,
    validateAppPermissionForm,
    type AppPermissionFormType,
    type RoleOption,
} from "@/views/AddAppPermission/utils";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import type {
    FamAccessControlPrivilegeCreateRequest,
    FamRoleGrantDto,
} from "fam-admin-mgmt-api/model";
import { AdminRoleAuthGroup, AppEnv } from "fam-admin-mgmt-api/model";
import {
    UserType,
    type FamUserRoleAssignmentCreateSchema,
} from "fam-app-acsctl-api/model";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";
import { useForm } from "vee-validate";
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const auth = useAuth();
const environments = new EnvironmentSettings();
const userSearchRef = ref<HTMLElement | null>(null);

const props = defineProps<AddAppPermissionRouteProps>();

if (!props.appId) {
    console.warn("Invalid or missing required query params");
    router.push("/");
}

const hasSubmitted = ref(false);
const userErrorMessage = computed(() => (hasSubmitted.value ? errors.value.users ?? "" : ""));
// Determine available user domains based on the logged-in user's type (IDIR or BCeID).
// IDIR users can grant both IDIR and BCeID users, while BCeID users can only grant BCeID users.
const availableDomains = computed(() => {
    return auth.authState.famLoginUser?.idpProvider === 'idir'
        ? [UserType.I, UserType.B]
        : [UserType.B];
    });
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

// Hoisted so it can also be used by "allowSelfSelection" below, not just
// within "rolesUnderSelectedApp" - the self-selection rule must key off
// which mutation this form will submit to (assignUserRoles vs
// delegatedAdminMutation), not just the application's environment.
const isDelegatedAdminOnly = computed(() =>
    isUserDelegatedAdminOnly(props.appId, adminUserAccessQuery.data.value)
);

const rolesUnderSelectedApp = computed(() => {
    if (!adminUserAccessQuery.data.value) return null;

    const adminUserAccess = adminUserAccessQuery.data.value;

    const availableRoles = isDelegatedAdminOnly.value
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

/**
 * POC: role options sourced from CSS instead of fam_role.
 * See .ai/keycloak-css-feasibility.md
 *
 * Resolves the CSS integration + environment for the selected FAM application by
 * matching on description, the same join the application dropdown uses.
 */
const cssApplicationsQuery = useQuery({
    queryKey: ["css-applications"],
    queryFn: () =>
        AdminMgmtApiService.cssIntegrationsApi
            .getCssApplications()
            .then((res) => res.data),
});

const cssApplicationForSelectedApp = computed(() => {
    const description = rolesUnderSelectedApp.value?.application.description;
    if (!description) return null;
    return (
        cssApplicationsQuery.data.value?.find(
            (cssApp) => cssApp.description === description
        ) ?? null
    );
});

const cssRolesQuery = useQuery({
    queryKey: ["css-application-roles", cssApplicationForSelectedApp],
    enabled: computed(() => Boolean(cssApplicationForSelectedApp.value)),
    queryFn: () =>
        AdminMgmtApiService.cssIntegrationsApi
            .getCssApplicationRoles(
                cssApplicationForSelectedApp.value!.integration_id,
                cssApplicationForSelectedApp.value!.environment
            )
            .then((res) => res.data),
});

/**
 * The role table's options — sourced from CSS only.
 *
 * CSS supplies which roles exist and, via composite membership against
 * HAS_DISTRICT_ROLE / HAS_FOREST_CLIENT, their scope type. Nothing is merged in
 * from fam_role, so the table shows exactly what CSS can express.
 *
 * Consequence: no display name and no description. A CSS role is a name and a
 * composite flag, so `display_name` falls back to the raw role name and the
 * description column is empty. That is the point of this configuration — it shows
 * what a CSS-only role table actually looks like. See .ai/keycloak-css-feasibility.md
 *
 * CSS expresses a display name by nesting roles: a human readable role composed of
 * the machine role code, which may itself be composed of scope markers. So
 * `display_name` is the outer role ("Submitter (CHR)") and `name` the code beneath
 * it ("CHR_FREP_EDITOR"), with scope resolved down the whole chain server-side.
 *
 * `description` stays empty — CSS has nowhere to store one.
 *
 * CSS has no FAM role_id, but the role table uses `id` for row identity — it is
 * how RoleSelectTable decides which row to expand. So each role gets a distinct
 * synthetic negative id, starting at -1000 to stay clear of the -999 sentinel used
 * by the fake "Delegated admin" row. These are not FAM role_ids, so nothing here
 * can be submitted to FAM's grant endpoint as-is.
 */
const cssRoleOptions = computed<RoleOption[]>(() =>
    (cssRolesQuery.data.value ?? []).map(
        (cssRole, index) =>
            ({
                id: -(1000 + index),
                name: cssRole.role_code ?? cssRole.name,
                display_name: cssRole.display_name ?? cssRole.name,
                description: null,
                role_type_district: cssRole.role_type_district,
                role_type_client: cssRole.role_type_client,
                forest_clients: [],
            }) as RoleOption
    )
);

// App admins (not delegated admins) may self-select on a non-FAM
// application's DEV/TEST instance - mirrors the backend guard's allowlist
// framing: check env === Dev || env === Test explicitly,
// do not invert to env !== Prod, so a missing/unset env fails closed.
const allowSelfSelection = computed(() => {
    const application = rolesUnderSelectedApp.value?.application;
    return (
        !isDelegatedAdminOnly.value &&
        !!application &&
        application.name !== FAM_APPLICATION_NAME &&
        (application.env === AppEnv.Dev || application.env === AppEnv.Test)
    );
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

// single-user select for delegated admin or multi-users select for regular users
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

const handleUserDomainChange = (userType: UserType) => {
    setFieldValue("domain", userType);
};

const handlePreUserDomainChange = (payload: {
    currentDomain: UserType;
    nextDomain: UserType;
    selectedUsersCount: number;
    approveChange: () => void;
    cancelChange: () => void;
}) => {
    if (payload.selectedUsersCount > 0) {
        confirm.require({
            group: "changeDomain",
            header: "Changing User Domain",
            rejectLabel: "Cancel",
            acceptLabel: "Continue",
            accept: () => payload.approveChange(),
            reject: () => payload.cancelChange(),
        });
    } else {
        // If no users have been selected yet, allow domain change without confirmation
        payload.approveChange();
    }
};

const handleSearchUsersSelected = (selectedUsers: SelectedUser[]) => {
    if (selectedUsers.length || meta.value.dirty) {
        setFieldValue("users", selectedUsers);
    }
};

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
const confirm = useConfirm();

/**
 * POC: grant the selected role in CSS rather than FAM.
 *
 * The role options come from CSS (see cssRoleOptions), so their `id` is a
 * synthetic negative — there is no FAM role_id to post to FAM's grant endpoint.
 * Scope-specific roles are created on demand by the API: selecting
 * CHR_FREP_EDITOR with districts DCC/DCS yields CHR_FREP_EDITOR_DISTRICT-DCC and
 * -DCS, which are created if absent and then assigned.
 *
 * CSS assigns one user at a time, so multiple selected users are submitted
 * sequentially. See .ai/keycloak-css-feasibility.md
 */
const cssAssignUserRoles = useMutation({
    mutationFn: async () => {
        const cssApp = cssApplicationForSelectedApp.value;
        if (!cssApp) throw new Error("No CSS integration for the selected application");
        if (!values.role) throw new Error("No role selected");

        const districtCodes = (values.districts ?? []).map((d) => d.org_unit_code);

        const responses = [];
        for (const user of values.users) {
            const res =
                await AdminMgmtApiService.cssIntegrationsApi.createCssUserRoleAssignment(
                    cssApp.integration_id,
                    cssApp.environment,
                    {
                        user_guid: user.guid ?? "",
                        user_type_code: values.domain,
                        role_name: values.role.name,
                        scope_type: districtCodes.length ? "DISTRICT" : null,
                        scope_values: districtCodes,
                    }
                );
            responses.push(...res.data);
        }
        return responses;
    },
    onSuccess: (results) => {
        isSubmitting.value = false;
        const failed = results.filter((r) => r.error_message);
        // eslint-disable-next-line no-console
        console.info("CSS role assignment result:", results);
        if (failed.length) {
            queryClient.setQueryData([AddAppUserPermissionErrorQuerykey], {
                error: new Error(
                    failed.map((r) => `${r.role_name}: ${r.error_message}`).join("; ")
                ),
                formData: values,
            });
            return;
        }
        activeTabIndex.value = 0;
        router.push({
            name: ManagePermissionsRoute.name,
            query: { appId: props.appId },
        });
    },
    onError: (error) => {
        isSubmitting.value = false;
        queryClient.setQueryData([AddAppUserPermissionErrorQuerykey], {
            error,
            formData: values,
        });
    },
});

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
            // POC: roles come from CSS, so the grant goes to CSS too.
            cssAssignUserRoles.mutate();
        } else {
            confirm.require({
                group: "addDelegatedAdmin",
                header: "Add a delegated admin",
                rejectLabel: "Cancel",
                acceptLabel: "Submit delegated admin",
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
    scrollToRef(userSearchRef);
};

</script>

<template>
    <div class="add-app-permission-container">
        <ConfirmDialog
            group="changeDomain"
        >
            <template #message>
                <p>
                    Changing the domain will remove the user{{
                        values.users.length > 1 ? "s" : ""
                    }} you've added. Are you sure you want to continue?
                </p>
            </template>
        </ConfirmDialog>
        <ConfirmDialog
            group="addDelegatedAdmin"
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
                        <div ref="userSearchRef">
                            <UserSearch
                                :app-id="appId"
                                :multi-user-mode="true"
                                :available-domains="availableDomains"
                                :helper-text="
                                    values.domain === UserType.I
                                        ? 'Search IDIR users by username, first name, or last name.'
                                        : 'Search BCeID users by username.'
                                "
                                search-button-label="Search"
                                :allow-self-selection="allowSelfSelection"
                                @pre-user-domain-change="handlePreUserDomainChange"
                                @user-domain-change="handleUserDomainChange"
                                @user-selection-update="handleSearchUsersSelected"
                            >
                                <template #formError>
                                    <span v-if="userErrorMessage" class="invalid-feedback">
                                        {{ userErrorMessage }}
                                    </span>
                                </template>
                            </UserSearch>
                        </div>
                    </StepContainer>
                    <StepContainer
                        title="User roles"
                        subtitle="Select a role for this user"
                        divider
                        v-if="cssRoleOptions.length"
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
                            :roleOptions="cssRoleOptions"
                            :is-delegated-admin-only="isDelegatedAdminOnly"
                            role-field-id="role"
                            forest-clients-field-id="forestClients"
                            districts-field-id="districts"
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
                            :model-value="values.expiryDate ?? undefined"
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

    .app-permission-form-container {
        margin-top: 3rem;

        padding: 0;
    }

    .invalid-feedback {
        display: block;
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
