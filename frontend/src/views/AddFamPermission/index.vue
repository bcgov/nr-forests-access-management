<script setup lang="ts">
import { ref, provide, computed, watch } from "vue";
import { useSelectUserManagement, SELECT_APP_ADMIN_USER_KEY } from "@/composables/useSelectUserManagement";
import { Field, Form } from "vee-validate";
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

const applicationListQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => getFamAdminApplications(data),
});

const formData = ref<AppAdminFormType>(getDefaultFormData());

// Use composable for single-user management
const grantUserManagement = useSelectUserManagement(false); // false = single-user mode
provide(SELECT_APP_ADMIN_USER_KEY, grantUserManagement);

const selectedUser = computed(() => {
  const users = grantUserManagement.userList.value;
  return users.length > 0 ? users[0] : null;
});

// Sync composable user to formData
watch(selectedUser, (newUser) => {
    console.log("Selected user changed:", newUser);
    formData.value.user = newUser;
});

// const handleUserVerification = (user: IdimProxyIdirInfoSchema) => {
//     if (formData.value) {
//         formData.value.user = user;
//     }
// };

const handleApplicationChange = (e: DropdownChangeEvent) => {
    if (formData.value) {
        formData.value.application = e.value;
    }
};

const isSubmitting = ref<boolean>(false);

const queryClient = useQueryClient();

const famPermissionMutation = useMutation({
    mutationFn: (payload: FamAppAdminCreateRequest) =>
        AdminMgmtApiService.applicationAdminApi.createApplicationAdmin(payload),
    onSuccess: (res) => {
        const userFullName = formatUserNameAndId(
            formData.value.user?.userId,
            formData.value.user?.firstName,
            formData.value.user?.lastName
        );
        const appName = formData.value.application?.description;
        const successMsg = `Admin privilege has been added to ${userFullName} for application ${appName}`;
        queryClient.setQueryData([AddAppAdminSuccessQueryKey], successMsg);
        router.push({
            name: ManagePermissionsRoute.name,
            query: {
                appId: 1,
                newFamAdminIds: [res.data.application_admin_id],
            },
        });
    },
    onError: (error) => {
        let errMsg = "";
        const userFullName = formatUserNameAndId(
            formData.value.user?.userId,
            formData.value.user?.firstName,
            formData.value.user?.lastName
        );
        const appName = formData.value.application?.description;

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
    console.log("Submitting form data:", formData.value);
    if (formData.value) {
        isSubmitting.value = true;
        const payload = generatePayload(formData.value);
        famPermissionMutation.mutate(payload);
    }
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
            <Form
                id="add-app-admin-form-id"
                v-slot="{ handleSubmit }"
                ref="form"
                v-if="formData"
                :validation-schema="validateAppAdminForm()"
                validate-on-submit
                class="col-sm-12 col-md-12 col-lg-10"
            >
            <!-- class="row" -->
                <!-- <form
                    id="add-fam-permission-form-id"
                    class="col-sm-12 col-md-12 col-lg-10"
                > -->
                    <StepContainer title="User information" divider>
                        <UserNameInput
                            class="user-name-text-input"
                            :domain="UserType.I"
                            :app-id="1"
                            helperText="Only IDIR users are allowed to be added as application admins"
                            :injection-key="SELECT_APP_ADMIN_USER_KEY"
                        />
                        <!-- @setUser="handleUserVerification" -->
                    </StepContainer>
                    <StepContainer title="Add application">
                        <Field
                            name="application"
                            v-slot="{ errorMessage }"
                            v-model="formData.application"
                        >
                            <Dropdown
                                required
                                label-text="Select an application this user will be able to manage"
                                class="application-dropdown"
                                name="application-dropdown"
                                :value="formData.application"
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
                            <span v-if="errorMessage" class="invalid-feedback">
                                {{ errorMessage }}
                            </span>
                        </Field>
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
                            @click="handleSubmit(onSubmit)"
                            :icon="CheckmarkIcon"
                            :is-loading="isSubmitting"
                        />
                    </div>
                <!-- </form> -->
            </Form>
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
