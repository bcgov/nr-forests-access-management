<script setup lang="ts">
import { ref } from "vue";
import { Field, Form } from "vee-validate";
import { isAxiosError } from "axios";
import { useRouter } from "vue-router";
import type { DropdownChangeEvent } from "primevue/dropdown";
import CheckmarkIcon from "@carbon/icons-vue/es/checkmark/16";
import BreadCrumbs from "@/components/UI/BreadCrumbs.vue";
import type { BreadCrumbType } from "@/types/BreadCrumbTypes";
import { ManagePermissionsRoute } from "@/router/routes";
import PageTitle from "@/components/common/PageTitle.vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { formatAxiosError, getUniqueApplications } from "@/utils/ApiUtils";
import {
    UserType,
    type FamAppAdminCreateRequest,
} from "fam-admin-mgmt-api/model";
import type { IdimProxyIdirInfoSchema } from "fam-app-acsctl-api/model";
import UserNameInput from "@/components/grantaccess/form/UserNameInput.vue";
import StepContainer from "@/components/UI/StepContainer.vue";
import Dropdown from "@/components/UI/Dropdown.vue";
import Button from "@/components/common/Button.vue";
import { formatUserNameAndId } from "@/utils/UserUtils";
import {
    FamPermissionErrorQueryKey,
    FamPermissionSuccessQueryKey,
    generatePayload,
    getDefaultFormData,
    validateFamPermissionForm,
    type FamPermissionFormType,
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
    select: (data) => getUniqueApplications(data),
});

const formData = ref<FamPermissionFormType>(getDefaultFormData());

const handleUserVerification = (user: IdimProxyIdirInfoSchema) => {
    if (formData.value) {
        formData.value.user = user;
    }
};

const handleApplicatoinChange = (e: DropdownChangeEvent) => {
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
        queryClient.setQueryData([FamPermissionSuccessQueryKey], successMsg);
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

        queryClient.setQueryData([FamPermissionErrorQueryKey], errMsg);
        router.push({ name: ManagePermissionsRoute.name, query: { appId: 1 } });
    },
    onSettled: () => {
        isSubmitting.value = false;
    },
    retry: 0,
});

const onSubmit = () => {
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
        <div class="form-container">
            <Form
                v-slot="{ handleSubmit }"
                ref="form"
                as="div"
                v-if="formData"
                :validation-schema="validateFamPermissionForm()"
                validate-on-submit
            >
                <form id="add-fam-permission-form-id">
                    <StepContainer title="User information" divider>
                        <UserNameInput
                            class="user-name-text-input"
                            :domain="UserType.I"
                            :user="formData.user"
                            :app-id="1"
                            @setVerifyResult="handleUserVerification"
                            helperText="Only IDIR users are allowed to be added as application admins"
                        />
                    </StepContainer>
                    <StepContainer
                        title="Add application"
                        subtitle="Select an application this user will be able to manage"
                    >
                        <Field
                            name="application"
                            v-slot="{ errorMessage }"
                            v-model="formData.application"
                        >
                            <Dropdown
                                class="application-dropdown"
                                name="application-dropdown"
                                :value="formData.application"
                                :options="applicationListQuery.data.value"
                                @change="handleApplicatoinChange"
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
                </form>
            </Form>
        </div>
    </div>
</template>
<style lang="scss">
.add-fam-permission-container {
    .form-container {
        margin-top: 3rem;
        width: 60%; // Temporary until we implement the grid system

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
