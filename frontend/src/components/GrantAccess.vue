<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import { selectedApplication } from '@/services/ApplicationState';
import type { FamApplicationRole, FamUserRoleAssignmentCreate } from 'fam-api';
import { onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';
import { Form as VeeForm, Field, ErrorMessage } from 'vee-validate';
import router from '@/router';
import { object, string } from 'yup';

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;
const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.
let applicationRoleOptions = ref<FamApplicationRole[]>([]);
const defaultFormData = {
    domain: domainOptions.BCEID,
    userId: null,
    forestClientNumber: null,
    role: null as unknown as FamApplicationRole,
    roleUI: null as unknown as FamApplicationRole,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();

const schema = object().shape({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    roleUI: object().required('Please select a value').nullable(),
    forestClientNumber: string().when('roleUI', {
        is: (role: any) => role?.role_type_code == 'A',
        then: string()
            .required('Forest Client number is required')
            .min(8, 'Forest Client number must be at least 8 characters')
            .nullable(),
    }),
});

onMounted(async () => {
    try {
        applicationRoleOptions.value = (
            await applicationsApi.getFamApplicationRoles(
                selectedApplication?.value?.application_id as number
            )
        ).data as FamApplicationRole[];
    } catch (error: unknown) {
        router.push('/application');
        return Promise.reject(error);
    }
});

function onlyDigit(evt: KeyboardEvent) {
    if (isNaN(parseInt(evt.key))) {
        evt.preventDefault();
    }
}

async function grantAccess() {
    const newUserRoleAssignmentPayload = toRequestPayload(formData.value);
    try {
        await userRoleAssignmentApi.createUserRoleAssignment(
            newUserRoleAssignmentPayload
        );
        useToast().success(
            `User "${newUserRoleAssignmentPayload.user_name}" is granted with "${formData.value.role.role_name}" access.`
        );
        formData.value = JSON.parse(JSON.stringify(defaultFormData)); // clone default input data.
        router.push('/manage');
    } catch (err: any) {
        return Promise.reject(err);
    }
}

function toRequestPayload(formData: any) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role.role_id,
        ...(formData.forestClientNumber
            ? {
                  forest_client_number: formData.forestClientNumber.padStart(
                      FOREST_CLIENT_INPUT_MAX_LENGTH,
                      '0'
                  ),
              }
            : {}),
    } as FamUserRoleAssignmentCreate;
    return request;
}

function statusSelected(evt: any) {
    formData.value.role = JSON.parse(evt.target.value);
}
</script>

<template>
    <PageTitle :displaySelectedApplication="true"></PageTitle>
    <VeeForm
        ref="form"
        v-slot="{ handleSubmit, errors, meta }"
        :validation-schema="schema"
        as="div"
    >
        <form
            id="grantAccessForm"
            class="form-container"
            @submit.prevent="handleSubmit($event, grantAccess)"
        >
            <div class="row">
                <div class="form-group col-md-3">
                    <label for="domainInput" class="control-label"
                        >Domain</label
                    >
                    <div>
                        <div class="form-check form-check-inline">
                            <Field
                                type="radio"
                                id="becidSelect"
                                name="domainRadioOptions"
                                class="form-check-input"
                                :value="domainOptions.BCEID"
                                v-model="formData.domain"
                                :checked="
                                    formData.domain === domainOptions.BCEID
                                "
                            />
                            <label class="form-check-label" for="becidSelect"
                                >BCeID</label
                            >
                        </div>
                        <div class="form-check form-check-inline">
                            <Field
                                type="radio"
                                id="idirSelect"
                                name="domainRadioOptions"
                                class="form-check-input"
                                :value="domainOptions.IDIR"
                                v-model="formData.domain"
                                :checked="
                                    formData.domain === domainOptions.IDIR
                                "
                            />
                            <label class="form-check-label" for="idirSelect"
                                >IDIR</label
                            >
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="form-group col-md-3">
                    <label for="userIdInput" class="control-label"
                        >User Id</label
                    ><span class="text-danger"> *</span>
                    <Field
                        type="text"
                        id="userIdInput"
                        class="form-control"
                        name="userId"
                        maxlength="20"
                        placeholder="User's Id"
                        v-model="formData.userId"
                        :validateOnChange="true"
                        :class="{ 'is-invalid': errors.userId }"
                    />
                    <ErrorMessage class="invalid-feedback" name="userId" />
                </div>
            </div>

            <div class="row">
                <div class="form-group col-md-5">
                    <label for="roleSelect" class="control-label">Role</label
                    ><span class="text-danger"> *</span>
                    <Field
                        id="roleSelect"
                        as="select"
                        name="roleUI"
                        class="form-select"
                        aria-label="Role Select"
                        v-model="formData.roleUI"
                        :class="{ 'is-invalid': errors.roleUI }"
                        @change="statusSelected"
                    >
                        <option
                            v-for="role in applicationRoleOptions"
                            :key="role.role_id"
                            :value="JSON.stringify(role)"
                        >
                            {{ role.role_name }}
                        </option>
                    </Field>
                    <ErrorMessage class="invalid-feedback" name="roleUI" />
                </div>
            </div>
            <div class="row" v-if="formData.role?.role_type_code == 'A'">
                <div class="form-group col-md-3">
                    <label for="forestClientInput" class="control-label"
                        >Forest Client</label
                    ><span class="text-danger"> *</span>
                    <Field
                        type="text"
                        name="forestClientNumber"
                        id="forestClientInput"
                        class="form-control"
                        :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH"
                        placeholder="Forest Client Id - 8 digits"
                        v-model="formData.forestClientNumber"
                        v-on:keypress="onlyDigit($event)"
                        :validateOnChange="true"
                        :class="{ 'is-invalid': errors.forestClientNumber }"
                    />
                    <ErrorMessage
                        class="invalid-feedback"
                        name="forestClientNumber"
                    />
                </div>
            </div>
            <div class="row gy-3">
                <div class="col-auto">
                    <button
                        type="submit"
                        id="grantAccessSubmit"
                        class="btn btn-primary mb-3"
                        :disabled="!meta.valid"
                    >
                        Grant Access
                    </button>
                </div>
            </div>
        </form>
    </VeeForm>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
