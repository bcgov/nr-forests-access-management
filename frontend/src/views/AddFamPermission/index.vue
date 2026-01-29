<script setup lang="ts">
import { ref, provide } from "vue";
import { useSelectUserManagement, SELECT_APP_ADMIN_USER_KEY } from "@/composables/useSelectUserManagement";
import { useForm } from "vee-validate";
import { isAxiosError } from "axios";
import { useRouter } from "vue-router";
import type { DropdownChangeEvent } from "primevue/dropdown";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import PageTitle from "@/components/UI/PageTitle.vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { formatAxiosError, getFamAdminApplications } from "@/utils/ApiUtils";
import {
    UserType,
    type FamAppAdminCreateRequest,
} from "fam-admin-mgmt-api/model";
import UserNameInput from "@/components/AddPermissions/UserNameSection.vue";
import StepContainer from "@/components/UI/StepContainer.vue";
import Dropdown from "@/components/UI/Dropdown.vue";
import Button from "@/components/UI/Button.vue";
import { formatUserNameAndId } from "@/utils/UserUtils";
import {
    AddAppAdminErrorQueryKey,
    AddAppAdminSuccessQueryKey,
    generatePayload,
    getDefaultFormData,
    NewAppAdminQueryParamKey,
    validateAppAdminForm,
    type AppAdminFormType,
} from "./utils";

const router = useRouter();

// Breadcrumb configuration
const crumbs: BreadCrumbType[] = [
    {
        label: "Manage permissions",
        routeName: ManagePermissionsRoute.name!,
    },
];

// Use composable for single-user user selection
const grantUserManagement = useSelectUserManagement(false); // false = single-user mode
provide(SELECT_APP_ADMIN_USER_KEY, grantUserManagement);

/**
 * Form setup using vee-validate's v4 useForm composable.
 * - validationSchema: Schema for form validation.
 * - initialValues: Default values for the form fields to be initialized.
 * Returns form handlers and state.
 * handleSubmit - function to handle form submission
 * errors - reactive object containing validation errors
 * values - reactive object containing form field values
 * setFieldValue - function to programmatically set field values
 */
const { handleSubmit, errors, values, setFieldValue, meta } = useForm<AppAdminFormType>({
    validationSchema: validateAppAdminForm(),
    initialValues: getDefaultFormData(),
});

// Flag to track if form has been submitted - controls error display
const hasSubmitted = ref<boolean>(false);

const queryClient = useQueryClient();
const applicationListQuery = useQuery({
    queryKey: ["admin-user-apps-privilege"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => getFamAdminApplications(data),
});

const handleApplicationChange = (e: DropdownChangeEvent) => {
    setFieldValue("application", e.value);
};

const isSubmitting = ref<boolean>(false);

const famPermissionMutation = useMutation({
    mutationFn: (payload: FamAppAdminCreateRequest) =>
        AdminMgmtApiService.applicationAdminApi.createApplicationAdmin(payload),
    onSuccess: (res) => {
        const userFullName = formatUserNameAndId(
            values.user?.userId,
            values.user?.firstName,
            values.user?.lastName
        );
        const appName = values.application?.description;
        const successMsg = `Admin privilege has been added to ${userFullName} for application ${appName}`;
        queryClient.setQueryData([AddAppAdminSuccessQueryKey], successMsg);
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: 1,
                [NewAppAdminQueryParamKey]: [res.data.application_admin_id],
            },
        });
    },
    onError: (error) => {
        let errMsg = "";
        const userFullName = formatUserNameAndId(
            values.user?.userId,
            values.user?.firstName,
            values.user?.lastName
        );
        const appName = values.application?.description;

        if (isAxiosError(error) && error.response?.status === 409) {
            errMsg = `${userFullName} is already a ${appName} admin`;
        } else {
            errMsg = `Failed to add ${userFullName} as a ${appName} admin`;
        }

        queryClient.setQueryData([AddAppAdminErrorQueryKey], errMsg);
        router.push({ name: ManagePermissionsRoute.name, query: { appId: 1 } });
    },
    onSettled: () => {
        isSubmitting.value = false;
    },
    retry: 0,
});

const onSubmit = () => {
    isSubmitting.value = true;
    famPermissionMutation.mutate(generatePayload(values));
};

// vee-validate onInvalid handler after form submission attempt.
// For displaying validation errors after first submit attempt.
// After v5 upgrade, can probably remove this and use better approach.
const onInvalid = () => {
  hasSubmitted.value = true;
};
</script>

<template>
    <div class="add-fam-permission-container">
        <BreadCrumbs :crumbs="crumbs" />
        <PageTitle
            title="Add application admin"
            subtitle="All fields are mandatory"
        />
        <div class="app-admin-form-container container-fluid">
            <form
                id="add-app-admin-form-id"
                class="col-sm-12 col-md-12 col-lg-10"
                @submit.prevent="handleSubmit(onSubmit, onInvalid)()"
            >
                <StepContainer title="User information" divider>
                    <UserNameInput
                        class="user-name-text-input"
                        :domain="UserType.I"
                        :app-id="1"
                        helperText="Only IDIR users are allowed to be added as application admins"
                        :injection-key="SELECT_APP_ADMIN_USER_KEY"
                    />
                </StepContainer>
                <StepContainer title="Add application">
                    <div>
                        <Dropdown
                            required
                            label-text="Select an application this user will be able to manage"
                            class="application-dropdown"
                            name="application-dropdown"
                            :value="values.application"
                            :options="applicationListQuery.data.value"
                            @change="handleApplicationChange"
                            option-label="description"
                            placeholder="Choose an application"
                            :is-fetching="
                                applicationListQuery.isLoading.value
                            "
                            :is-error="applicationListQuery.isError.value"
                            :error-msg="
                                isAxiosError(
                                    applicationListQuery.error.value
                                )
                                    ? formatAxiosError(
                                          applicationListQuery.error.value
                                      )
                                    : 'Failed to fetch data.'
                            "
                        />
                        <span v-if="hasSubmitted && errors.application" class="invalid-feedback">
                            {{ errors.application }}
                        </span>
                    </div>
                </StepContainer>
                <div class="button-group">
                    <Button
                        label="Back"
                        severity="secondary"
                        @click="
                            () =>
                                router.push({
                                    name: ManagePermissionsRoute.name,
                                    query: { appId: 1 },
                                })
                        "
                    />
                    <Button
                        :label="`Create Application Admin`"
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
.add-fam-permission-container {
    .app-admin-form-container {
        margin-top: 3rem;
        padding: 0;

        .invalid-feedback {
            display: block;
        }
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
