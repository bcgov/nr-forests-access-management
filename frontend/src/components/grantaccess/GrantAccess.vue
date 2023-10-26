<script setup lang="ts">
import router from '@/router';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { onMounted, ref } from 'vue';
import { number, object, string } from 'yup';

import Button from '@/components/common/Button.vue';
import ForestClientCard from '@/components/grantaccess/ForestClientCard.vue';
import UserIdentityCard from '@/components/grantaccess/UserIdentityCard.vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import RadioButton from 'primevue/radiobutton';

import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    selectedApplication,
    selectedApplicationDisplayText,
} from '@/store/ApplicationState';

import LoadingState from '@/store/LoadingState';
import {
    FamForestClientStatusType,
    type FamApplicationRole,
    type FamForestClient,
    type IdimProxyIdirInfo,
    type FamUserRoleAssignmentCreate,
} from 'fam-api';

import { IconSize } from '@/enum/IconEnum';
import { Severity } from '@/enum/SeverityEnum';
import { pushNotification } from '@/store/NotificationState';

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;

const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.

const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumberList: [],
    role_id: null as number | null,
};

const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input

const forestClientNumberVerifyErrors = ref([] as Array<string>);

const formValidationSchema = object({
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
                    .nullable()
                    .transform((curr, orig) => (orig === '' ? null : curr)) // Accept either null or value
                    .matches(
                        /^\d{8}(,\s?\d{8})*$/,
                        'Each Forest Client ID must be 8 digits long'
                    ),
        })
        .nullable(),
});

let applicationRoleOptions = ref<FamApplicationRole[]>([]);
const forestClientData = ref<FamForestClient[]>([]);
const verifiedUserIdentity = ref<IdimProxyIdirInfo | null>(null);

const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const forestClientApi = apiServiceFactory.getForestClientApi();
const idirBceidProxyApi = apiServiceFactory.getIdirBceidProxyApi();
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();

onMounted(async () => {
    applicationRoleOptions.value = (
        await applicationsApi.getFamApplicationRoles(
            selectedApplication.value?.application_id as number
        )
    ).data;
});

const isIdirDomainSelected = () => {
    return formData.value.domain === domainOptions.IDIR;
};

function userDomainChange() {
    resetVerifiedUserIdentity();
    formData.value.userId = '';
}

const getSelectedRole = (): FamApplicationRole | undefined => {
    return applicationRoleOptions.value?.find(
        (item) => item.role_id === formData.value.role_id
    );
};

const isAbstractRoleSelected = () => {
    return getSelectedRole()?.role_type_code == 'A';
};

function userIdChange() {
    resetVerifiedUserIdentity();
    resetForestClientNumberData();
}

function resetVerifiedUserIdentity() {
    verifiedUserIdentity.value = null;
}

function resetForestClientNumberData() {
    formData.value['forestClientNumber'] = '';
    forestClientNumberVerifyErrors.value = [];
}

function resetForm() {
    formData.value = defaultFormData;
}

function cancelForm() {
    resetForm();
    router.push('/dashboard');
}

async function verifyIdentity(userId: string, domain: string) {
    if (domain == domainOptions.BCEID) return; // IDIR search currently, no BCeID yet.

    verifiedUserIdentity.value = (
        await idirBceidProxyApi.idirSearch(userId)
    ).data;
}

async function verifyForestClientNumber(forestClientNumber: string) {
    forestClientNumberVerifyErrors.value = [];
    let forestNumbers = forestClientNumber.split(/[ ,]+/);

    for (const item of forestNumbers) {
        if (isNaN(parseInt(item))) {
            forestClientNumberVerifyErrors.value.push(
                `Client ID ${item}  is invalid and cannot be added.`
            );
        }
        await forestClientApi
            .search(item)
            .then((result) => {
                if (!result.data[0]) {
                    forestClientNumberVerifyErrors.value.push(
                        `Client ID ${item}  is invalid and cannot be added.`
                    );
                    return;
                }
                if (
                    result.data[0].status?.status_code !==
                    FamForestClientStatusType.A
                ) {
                    forestClientNumberVerifyErrors.value.push(
                        `Client ID ${item} is inactive and cannot be added.`
                    );
                    return;
                }
                if (
                    isForestClientNumberNotAdded(
                        result.data[0].forest_client_number
                    )
                ) {
                    forestClientData.value.push(result.data[0]);
                    forestNumbers = forestNumbers.filter(
                        (number) => number !== item
                    ); //Remove successfully added numbers so the user can edit in the input only errored ones
                } else {
                    forestClientNumberVerifyErrors.value.push(
                        `Client ID ${item} has already been added.`
                    );
                }
            })
            .catch(() => {
                forestClientNumberVerifyErrors.value.push(
                    `An error has occured. Client ID ${item} could not be added.`
                );
            });
    }
    //The input is updated with only the numbers that have errored out. The array is converted to a string values comma separated
    formData.value['forestClientNumber'] = forestNumbers.toString();
}

function isForestClientNumberNotAdded(forestClientNumber: string) {
    return !forestClientData.value.find(
        (item) => forestClientNumber === item.forest_client_number
    );
}

/*
Two verifications are cunnretly in place: userId and forestClientNumber.
*/
function areVerificationsPassed() {
    return (
        // userId verification.
        (!isIdirDomainSelected() ||
            (isIdirDomainSelected() && verifiedUserIdentity.value?.found)) &&
        // forestClientNumber verification
        (!isAbstractRoleSelected() ||
            (isAbstractRoleSelected() &&
                forestClientData.value?.[0]?.status?.status_code ==
                    FamForestClientStatusType.A))
    );
}

function toRequestPayload(
    formData: any,
    forestClientNumber: FamForestClient | null
) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role_id,
        ...(forestClientNumber
            ? {
                  forest_client_number:
                      forestClientNumber.forest_client_number.padStart(
                          FOREST_CLIENT_INPUT_MAX_LENGTH,
                          '0'
                      ),
              }
            : {}),
    } as FamUserRoleAssignmentCreate;
    return request;
}

async function handleSubmit() {
    if (forestClientData.value.length > 0) {
        const successList: string[] = [];
        const warningList: string[] = [];
        const errorList: string[] = [];
        for (const item of forestClientData.value) {
            const data = toRequestPayload(formData.value, item);

            await userRoleAssignmentApi
                .createUserRoleAssignment(data as FamUserRoleAssignmentCreate)
                .then(() => {
                    successList.push(item.forest_client_number);
                })
                .catch((error) => {
                    if (error.response?.status === 409) {
                        warningList.push(item.forest_client_number);
                    } else {
                        errorList.push(item.forest_client_number);
                    }
                });
        }

        if (successList.length > 0) {
            pushNotification(
                Severity.success,
                `${
                    formData.value.userId
                } was successfully added with Client IDs: ${successList.join(
                    ', '
                )}`
            );
        }
        if (warningList.length > 0) {
            pushNotification(
                Severity.warning,
                `${
                    formData.value.userId
                } already exists with Client IDs: ${warningList.join(', ')}`
            );
        }
        if (errorList.length > 0) {
            pushNotification(
                Severity.error,
                `${
                    formData.value.userId
                } was not added with Client IDs: ${errorList.join(', ')}`
            );
        }

        router.push('/dashboard');
    } else {
        const data = toRequestPayload(formData.value, null);
        await userRoleAssignmentApi
            .createUserRoleAssignment(data)
            .then(() => {
                pushNotification(
                    Severity.success,
                    `${
                        formData.value.userId
                    } was successfully added with the role ${
                        getSelectedRole()?.role_name
                    }`
                );
            })
            .catch((error) => {
                if (error.response?.status === 409) {
                    pushNotification(
                        Severity.warning,
                        `${
                            formData.value.userId
                        } already exists with the role ${
                            getSelectedRole()?.role_name
                        }`
                    );
                } else {
                    pushNotification(
                        Severity.error,
                        `An error has occured. ${
                            formData.value.userId
                        } could not be added with the role ${
                            getSelectedRole()?.role_name
                        }.`
                    );
                }
            });
        router.push('/dashboard');
    }
}

function removeForestClientFromList(index: number) {
    forestClientData.value.splice(index, 1);
}
</script>

<template>
    <VeeForm
        ref="form"
        v-slot="{ errors, meta }"
        :validation-schema="formValidationSchema"
        as="div"
    >
        <PageTitle
            title="Grant access to a user"
            :subtitle="'You are editing in ' + selectedApplicationDisplayText"
        />
        <div class="page-body">
            <div class="row">
                <form id="grantAccessForm" class="form-container">
                    <div class="row">
                        <label> Select user's domain </label>
                        <div class="px-0">
                            <RadioButton
                                v-model="formData.domain"
                                :checked="isIdirDomainSelected()"
                                inputId="idirSelect"
                                name="domainRadioOptions"
                                :value="domainOptions.IDIR"
                                @change="userDomainChange()"
                            />
                            <label class="mx-2" for="idirSelect">IDIR</label>
                        </div>
                        <div class="px-0">
                            <RadioButton
                                v-model="formData.domain"
                                inputId="becidSelect"
                                name="domainRadioOptions"
                                :value="domainOptions.BCEID"
                                @change="userDomainChange()"
                            />
                            <label class="mx-2" for="becidSelect">BCeID</label>
                        </div>
                    </div>

                    <div class="row">
                        <label for="userIdInput"
                            >Type user's id
                            <span class="text-danger"> *</span></label
                        >
                        <div class="mt-0 col-md-3 px-0">
                            <Field
                                name="userId"
                                :validateOnChange="true"
                                v-model="formData.userId"
                                v-slot="{ field }"
                            >
                                <InputText
                                    id="userIdInput"
                                    :placeholder="
                                        formData.domain === 'I'
                                            ? 'Type user\'s IDIR'
                                            : 'Type user\'s BCeID'
                                    "
                                    :validateOnChange="true"
                                    class="w-100"
                                    type="text"
                                    maxlength="20"
                                    v-bind="field"
                                    @input="userIdChange()"
                                    :class="{ 'is-invalid': errors.userId }"
                                />
                            </Field>
                            <ErrorMessage
                                class="invalid-feedback"
                                name="userId"
                            />
                        </div>

                        <!-- show "Verify" button only if (all applied):
                                * domain is IDIR (for now, BCeID is not availabe for verify yet)
                                * userId field is entered.
                                * userId entered does not contains basic validation errors.
                            -->
                        <div
                            class="col-md-2"
                            v-if="
                                formData.domain === domainOptions.IDIR &&
                                formData.userId &&
                                errors.userId == undefined
                            "
                        >
                            <Button
                                class="button"
                                outlined
                                aria-label="Verify user IDIR"
                                :name="'verifyIdir'"
                                :label="'Verify'"
                                :loading-label="'Verifying...'"
                                @click="
                                    verifyIdentity(
                                        formData.userId,
                                        formData.domain
                                    )
                                "
                                :disabled="LoadingState.isLoading.value"
                            >
                            </Button>
                        </div>
                    </div>

                    <div class="row" v-if="verifiedUserIdentity">
                        <div class="col-md-5 px-0">
                            <UserIdentityCard
                                :userIdentity="verifiedUserIdentity"
                            ></UserIdentityCard>
                        </div>
                    </div>

                    <div class="row">
                        <div class="px-0 col-md-6">
                            <label
                                >Assign a role
                                {{
                                    formData.userId
                                        ? 'to ' + formData.userId
                                        : ''
                                }}<span class="text-danger"> *</span></label
                            >

                            <Field
                                name="role_id"
                                aria-label="Role Select"
                                v-slot="{ field, handleChange }"
                                v-model="formData.role_id"
                            >
                                <Dropdown
                                    :options="applicationRoleOptions"
                                    optionLabel="role_name"
                                    optionValue="role_id"
                                    :modelValue="field.value"
                                    placeholder="Choose an option"
                                    class="w-100"
                                    style="width: 100% !important"
                                    v-bind="field.value"
                                    @update:modelValue="handleChange"
                                    @change="resetForestClientNumberData()"
                                    :class="{
                                        'is-invalid': errors.role_id,
                                    }"
                                >
                                </Dropdown>
                            </Field>
                            <ErrorMessage
                                class="invalid-feedback"
                                name="role_id"
                            >
                            </ErrorMessage>
                        </div>
                    </div>

                    <div v-if="isAbstractRoleSelected()">
                        <div class="row mb-0">
                            <div class="px-0 col-md-6">
                                <label for="forestClientInput"
                                    >User’s Client ID (8 digits)
                                    <span class="text-danger"> *</span></label
                                >
                            </div>
                        </div>
                        <div class="row pt-0 mt-0">
                            <div class="px-0 col-4">
                                <Field
                                    name="forestClientNumber"
                                    v-slot="{ field, meta, handleChange }"
                                    v-model="formData.forestClientNumber"
                                >
                                    <InputText
                                        id="forestClientInput"
                                        placeholder="Enter and verify the client ID"
                                        @update:modelValue="handleChange"
                                        v-bind:disabled="
                                            LoadingState.isLoading.value
                                        "
                                        :validateOnChange="true"
                                        v-bind="field"
                                        class="w-100"
                                        @input="resetForestClientNumberData()"
                                        :class="{
                                            'is-invalid':
                                                errors.forestClientNumber ||
                                                forestClientNumberVerifyErrors.length >
                                                    0,
                                        }"
                                    ></InputText>
                                </Field>
                                <ErrorMessage
                                    class="invalid-feedback"
                                    name="forestClientNumber"
                                />
                                <small
                                    class="helper-text"
                                    v-if="
                                        !errors.forestClientNumber &&
                                        forestClientNumberVerifyErrors.length ===
                                            0
                                    "
                                    >Add and verify the Client IDs. Add multiple
                                    numbers by separating them with
                                    commas</small
                                >
                                <small
                                    class="invalid-feedback"
                                    v-for="error in forestClientNumberVerifyErrors"
                                >
                                    {{ error }}
                                </small>
                            </div>
                            <div class="pr-1 col-2">
                                <Button
                                    outlined
                                    aria-label="Add Client Numbers"
                                    :name="'verifyFC'"
                                    :label="'Add Client Numbers'"
                                    :loading-label="'Verifying...'"
                                    @click="
                                        verifyForestClientNumber(
                                            formData.forestClientNumber as string
                                        )
                                    "
                                    v-bind:disabled="
                                        formData.forestClientNumber?.length <
                                            FOREST_CLIENT_INPUT_MAX_LENGTH ||
                                        !!errors.forestClientNumber ||
                                        LoadingState.isLoading.value
                                    "
                                >
                                    <Icon icon="add" :size="IconSize.small" />
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div v-if="forestClientData.length > 0" class="row">
                        <div class="col-md-5 px-0">
                            <ForestClientCard
                                :forestClientData="forestClientData"
                                @remove-item="removeForestClientFromList"
                            ></ForestClientCard>
                        </div>
                    </div>

                    <div class="row gy-1 my-0">
                        <div class="col-auto px-0 button-stack">
                            <Button
                                type="button"
                                id="grantAccessCancel"
                                class="mb-3 button"
                                severity="secondary"
                                label="Cancel"
                                :disabled="LoadingState.isLoading.value"
                                @click="cancelForm()"
                            ></Button>
                            <Button
                                type="button"
                                id="grantAccessSubmit"
                                class="m-3 button"
                                label="Submit Application"
                                :disabled="
                                    !(meta.valid && areVerificationsPassed()) ||
                                    LoadingState.isLoading.value
                                "
                                @click="handleSubmit()"
                                ><Icon icon="checkmark" :size="IconSize.small"
                            /></Button>
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

.helper-text {
    font-size: 0.75rem;
    font-style: normal;
    font-weight: 400;
    line-height: 1rem;
    letter-spacing: 0.02rem;
}

.button {
    width: 7.875rem;
}

.button-stack {
    Button {
        width: 15rem;
    }
}
</style>
