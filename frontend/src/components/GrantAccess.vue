<script setup lang="ts">
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    selectedApplication,
    selectedApplicationDisplayText,
    grantAccessFormData,
} from '@/store/ApplicationState';
import type {
    FamApplicationRole,
    FamForestClient,
    FamUserRoleAssignmentCreate,
} from 'fam-api';
import { onMounted, ref } from 'vue';
import { Form as VeeForm, Field, ErrorMessage } from 'vee-validate';
import router from '@/router';
import { number, object, string } from 'yup';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown, { type DropdownChangeEvent } from 'primevue/dropdown';
import RadioButton from 'primevue/radiobutton';

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;
const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.
let applicationRoleOptions = ref<FamApplicationRole[]>([]);
let forestClient: FamForestClient[] | null = null;
let loading = ref<boolean>(false);
let userLoaded = ref<boolean>(false);
let invalidForestClient = ref<boolean>(false);
const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumber: '',
    role_id: null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const forestClientApi = apiServiceFactory.getForestClientApi();

const schema = object({
    userId: string()
        .required('User ID is required')
        .min(2, 'User ID must be at least 2 characters')
        .nullable(),
    role_id: number().required('Please select a value'),
    forestClientNumber: string()
        .when('role_id', {
            is: (_role_id: number) => isAbstractRoleSelected(),
            then: () =>
                string()
                    .required('Forest Client number is required')
                    .min(8, 'Forest Client ID must be 8 characters long'),
        })
        .nullable(),
});

onMounted(async () => {
    try {
        applicationRoleOptions.value = (
            await applicationsApi.getFamApplicationRoles(
                selectedApplication?.value?.application_id as number
            )
        ).data as FamApplicationRole[];
        if (grantAccessFormData.value) {
            let formTemp = {
                domain: grantAccessFormData.value.user_type_code,
                userId: grantAccessFormData.value.user_name,
                forestClientNumber:
                    grantAccessFormData.value.forest_client_number,
                role_id: grantAccessFormData.value.role_id,
            };

            if (grantAccessFormData.value.user_name) userLoaded.value = true;

            formData.value = JSON.parse(JSON.stringify(formTemp));
            invalidForestClient.value = isAbstractRoleSelected();
        }
    } catch (error: unknown) {
        router.push('/dashboard');
        return Promise.reject(error);
    }
});

function onlyDigit(evt: KeyboardEvent) {
    if (isNaN(parseInt(evt.key))) {
        evt.preventDefault();
    }
}

async function submitForm() {
    grantAccessFormData.value = toRequestPayload(formData.value);
    router.push('/summary');
}

function toRequestPayload(formData: any) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role_id,
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

function onRoleSelected(evt: DropdownChangeEvent) {
    forestClient = null;
    formData.value.forestClientNumber = '';
    invalidForestClient.value = isAbstractRoleSelected();
}

async function getForestClientNumber(forestClientNumber: string) {
    loading.value = true;
    try {
        forestClient = (await forestClientApi.search(forestClientNumber)).data;
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
        loading.value = false;
        if (forestClient?.[0]?.status?.description !== 'Active') {
            invalidForestClient.value = true;
        } else {
            invalidForestClient.value = false;
        }
    }
}

function getUserId(userId: string) {
    //TODO: Remove this timeout and replace with the call to the API that validates the user ID
    loading.value = true;
    setTimeout(() => {
        loading.value = false;
        userLoaded.value = true;
    }, 1500);
}

function forestClientNumberChange() {
    invalidForestClient.value = true;
    forestClient = null;
}

function userIdChange() {
    userLoaded.value = false;
    forestClientNumberChange();
}

const getSelectedRole = (): FamApplicationRole | undefined => {
    return applicationRoleOptions.value.find(
        (item) => item.role_id === formData.value.role_id
    );
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.role_type_code == 'A';
};
</script>

<template>
    <VeeForm
        ref="form"
        v-slot="{ handleSubmit, errors, meta }"
        :validation-schema="schema"
        as="div"
    >
        <PageTitle
            title="Grant access to a user"
            :subtitle="'You are editing in ' + selectedApplicationDisplayText"
        />
        <div class="page-body">
            <div class="row">
                <form
                    id="grantAccessForm"
                    class="form-container"
                    @submit.prevent="handleSubmit($event, submitForm)"
                >
                    <div class="row">
                        <div class="form-group col-md-3 px-0">
                            <label for="domainInput" class="control-label"
                                >Select user's domain</label
                            >
                            <div>
                                <div class="flex align-items-center">
                                    <RadioButton
                                        v-model="formData.domain"
                                        :checked="
                                            formData.domain ===
                                            domainOptions.IDIR
                                        "
                                        inputId="idirSelect"
                                        name="domainRadioOptions"
                                        :value="domainOptions.IDIR"
                                        class="p-radiobutton"
                                    />
                                    <label
                                        class="mx-2 form-check-label"
                                        for="idirSelect"
                                        >IDIR</label
                                    >
                                </div>
                                <div class="flex align-items-center">
                                    <RadioButton
                                        v-model="formData.domain"
                                        :checked="
                                            formData.domain ===
                                            domainOptions.IDIR
                                        "
                                        inputId="becidSelect"
                                        name="domainRadioOptions"
                                        :value="domainOptions.BCEID"
                                        class="p-radiobutton"
                                    />
                                    <label
                                        class="mx-2 form-check-label"
                                        for="becidSelect"
                                        >BCeID</label
                                    >
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="row mb-0">
                            <label for="userIdInput" class="control-label px-0"
                                >Type user's domain name
                                <span class="text-danger"> *</span></label
                            >
                        </div>

                        <div class="row mt-0">
                            <div class="col-md-3 px-0">
                                <Field
                                    id="userIdInput"
                                    class="form-control"
                                    name="userId"
                                    :validateOnChange="true"
                                    v-model="formData.userId"
                                    v-slot="{ field }"
                                >
                                    <InputText
                                        :placeholder="
                                            formData.domain === 'I'
                                                ? 'Type user\'s IDIR'
                                                : 'Type user\'s BCeID'
                                        "
                                        :validateOnChange="true"
                                        class="w-100 p-inputtext"
                                        type="text"
                                        maxlength="20"
                                        v-bind="field"
                                        @input="userIdChange()"
                                        :class="{ 'is-invalid': errors.userId }"
                                    ></InputText>
                                </Field>
                                <ErrorMessage
                                    class="invalid-feedback"
                                    name="userId"
                                />
                            </div>
                            <div class="col-md-3" v-if="!userLoaded">
                                <Button
                                    class="button p-button-tertiary p-button-outlined"
                                    @click="getUserId('4')"
                                    v-bind:disabled="
                                        formData.userId?.length < 2 || loading
                                    "
                                >
                                    <div class="w-100">
                                        <div v-if="loading">
                                            <span> Loading... </span>
                                        </div>
                                        <div v-else>Verify</div>
                                    </div></Button
                                >
                            </div>
                        </div>
                    </div>

                    <div class="row" v-if="userLoaded">
                        <div class="form-group col-md-3 px-0">
                            <label for="roleSelect" class="control-label px-0"
                                >Assign a role
                                {{
                                    formData.userId
                                        ? 'to ' + formData.userId
                                        : ''
                                }}<span class="text-danger"> *</span></label
                            >
                            <Field
                                id="roleSelect"
                                class="form-select"
                                name="role_id"
                                aria-label="Role Select"
                                v-slot="{ field, handleChange }"
                                v-model="formData.role_id"
                                @change="onRoleSelected"
                            >
                                <Dropdown
                                    :options="applicationRoleOptions"
                                    optionLabel="role_name"
                                    optionValue="role_id"
                                    :modelValue="field.value"
                                    placeholder="Choose an option"
                                    class="application-dropdown w-100"
                                    v-bind="field.value"
                                    @update:modelValue="handleChange"
                                    :class="{ 'is-invalid': errors.role_id }"
                                >
                                </Dropdown>
                            </Field>
                            <ErrorMessage
                                class="invalid-feedback"
                                name="role_id"
                            />
                        </div>
                    </div>
                    <div v-if="isAbstractRoleSelected()">
                        <div class="row mb-0">
                            <label
                                for="forestClientInput"
                                class="control-label label px-0"
                                >Type user’s Forest Client ID (8 characters)
                                <span class="text-danger"> *</span></label
                            >
                        </div>

                        <div class="row mt-0">
                            <div class="form-group col-md-3 px-0">
                                <Field
                                    name="forestClientNumber"
                                    id="forestClientInput"
                                    class="form-control"
                                    v-slot="{ field, handleChange }"
                                    v-model="formData.forestClientNumber"
                                >
                                    <InputText
                                        :maxlength="
                                            FOREST_CLIENT_INPUT_MAX_LENGTH
                                        "
                                        placeholder="Forest Client Id - 8 digits"
                                        @update:modelValue="handleChange"
                                        v-bind:disabled="loading"
                                        :validateOnChange="true"
                                        v-bind="field"
                                        class="w-100"
                                        v-on:keypress="onlyDigit($event)"
                                        @input="forestClientNumberChange()"
                                        :class="{
                                            'is-invalid':
                                                errors.forestClientNumber,
                                        }"
                                    ></InputText>
                                </Field>
                                <ErrorMessage
                                    class="invalid-feedback"
                                    name="forestClientNumber"
                                />
                            </div>
                            <div class="col-md-2">
                                <Button
                                    class="button p-button-tertiary p-button-outlined"
                                    @click="
                                        getForestClientNumber(
                                            formData.forestClientNumber
                                        )
                                    "
                                    v-bind:disabled="
                                        formData.forestClientNumber?.length <
                                            8 || loading
                                    "
                                >
                                    <div class="w-100">
                                        <div v-if="loading">
                                            <span> Loading... </span>
                                        </div>
                                        <div v-else>Verify</div>
                                    </div>
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div class="row" v-if="forestClient">
                        <div class="form-group col-md-5 px-0">
                            <ForestClientCard
                                :text="forestClient?.[0]?.client_name"
                                :status="forestClient?.[0]?.status"
                            ></ForestClientCard>
                        </div>
                    </div>

                    <div class="row gy-3 my-0" v-if="meta.valid">
                        <div class="col-auto px-0">
                            <Button
                                type="button"
                                id="grantAccessSubmit"
                                class="mb-3 button p-button"
                                label="Submit"
                                @click="submitForm()"
                            ></Button>
                            <Button
                                class="m-3 button"
                                outlined
                                label="Cancel"
                                @click="$router.go(-1)"
                            ></Button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </VeeForm>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.text-danger {
    font-weight: normal;
}

.button {
    width: 126px;
}
</style>
