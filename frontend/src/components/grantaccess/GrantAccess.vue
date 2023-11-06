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
    forestClientNumber: '',
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
    forestClientData.value = [];
    forestClientNumberVerifyErrors.value = [];
}

function cancelForm() {
    formData.value = defaultFormData;
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
    forestClientData: FamForestClient | null
) {
    const request = {
        user_name: formData.userId,
        user_type_code: formData.domain,
        role_id: formData.role_id,
        ...(forestClientData
            ? {
                  forest_client_number:
                      forestClientData.forest_client_number.padStart(
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
    }
    router.push('/dashboard');
}

function removeForestClientFromList(index: number) {
    forestClientData.value.splice(index, 1);
}
</script>

<template>
    <PageTitle
        title="Add user permission"
        subtitle="Add a new permission to a user. All fields are mandatory unless noted"
    />
    <VeeForm
        ref="form"
        v-slot="{ errors, meta }"
        :validation-schema="formValidationSchema"
        as="div"
    >
        <div class="page-body">
            <form id="grantAccessForm" class="form-container">
                <StepContainer
                    title="User information"
                    :subtitle="`Enter the user information to add a new user to ${selectedApplicationDisplayText}`"
                >
                    <div class="user-radio-group">
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
                    <div class="input-with-verify-field">
                        <div>
                            <label for="userIdInput">Username</label>
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
                                    class="w-100 custom-input"
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
                            <small
                                id="userIdInput-helper"
                                class="helper-text"
                                v-if="!errors.userId"
                                >Enter and verify the username for this
                                user</small
                            >
                        </div>
                        <div
                            v-if="formData.domain === 'I'"
                            class="no-label-column"
                        >
                            <Button
                                class="button w-100"
                                aria-label="Verify user IDIR"
                                :name="'verifyIdir'"
                                :label="'Verify'"
                                @click="
                                    verifyIdentity(
                                        formData.userId,
                                        formData.domain
                                    )
                                "
                                :disabled="
                                    LoadingState.isLoading.value ||
                                    formData.domain !== domainOptions.IDIR ||
                                    !formData.userId ||
                                    errors.userId !== undefined
                                "
                                ><Icon
                                    icon="search--locate"
                                    :size="IconSize.small"
                                />
                            </Button>
                        </div>
                    </div>

                    <div class="col-md-5 px-0" v-if="verifiedUserIdentity">
                        <UserIdentityCard
                            :userIdentity="verifiedUserIdentity"
                        ></UserIdentityCard>
                    </div>
                </StepContainer>

                <StepContainer
                    title="Add user roles"
                    subtitle="Enter a specific role for this user"
                    :divider="isAbstractRoleSelected()"
                >
                    <label>Assign a role to the user</label>

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
                            class="w-100 custom-input"
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
                    <ErrorMessage class="invalid-feedback" name="role_id">
                    </ErrorMessage>
                </StepContainer>

                <StepContainer
                    v-if="isAbstractRoleSelected()"
                    title="Organization information"
                    subtitle="Associate one or more Client IDs to this user"
                    :divider="false"
                >
                    <div class="input-with-verify-field">
                        <div>
                            <label for="forestClientInput"
                                >User’s Client ID (8 digits)
                            </label>
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
                                    class="w-100 custom-input"
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
                                id="forestClientInput-help"
                                class="helper-text"
                                v-if="
                                    !errors.forestClientNumber &&
                                    forestClientNumberVerifyErrors.length === 0
                                "
                                >Add and verify the Client IDs. Add multiple
                                numbers by separating them with commas</small
                            >
                            <small
                                class="invalid-feedback"
                                v-for="error in forestClientNumberVerifyErrors"
                            >
                                {{ error }}
                            </small>
                        </div>
                        <div class="no-label-column">
                            <Button
                                class="w-100"
                                aria-label="Add Client Numbers"
                                :name="'verifyFC'"
                                :label="'Add Client Numbers'"
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

                    <ForestClientCard
                        v-if="forestClientData.length > 0"
                        class="px-0"
                        :forestClientData="forestClientData"
                        @remove-item="removeForestClientFromList"
                    />
                </StepContainer>

                <div class="button-stack">
                    <Button
                        type="button"
                        id="grantAccessCancel"
                        class="button w100"
                        severity="secondary"
                        label="Cancel"
                        :disabled="LoadingState.isLoading.value"
                        @click="cancelForm()"
                        >&nbsp;</Button
                    >
                    <Button
                        type="button"
                        id="grantAccessSubmit"
                        class="button w100"
                        label="Submit Application"
                        :disabled="
                            !(meta.valid && areVerificationsPassed()) ||
                            LoadingState.isLoading.value
                        "
                        @click="handleSubmit()"
                        ><Icon icon="checkmark" :size="IconSize.small"
                    /></Button>
                </div>
            </form>
        </div>
    </VeeForm>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.text-danger {
    font-weight: normal;
}

.button {
    width: 7.875rem;
}

.button-stack {
    padding: 0;
    margin-top: 3rem;
    margin-bottom: 2.5rem;
    gap: 1rem;
    width: 100%;
    display: inline-grid;
    grid-template-columns: 1fr 1fr;
    Button {
        width: auto !important;
    }
}

.input-with-verify-field {
    padding: 0;
    display: block;
    width: 100%;
}
.no-label-column {
    margin-top: 1.5rem;
}

.user-radio-group {
    margin-bottom: 1.5rem;
}

.custom-input {
    max-height: 2.813rem !important;
}

@media (min-width: 390px) {
    .input-with-verify-field {
        display: inline-grid;
        grid-template-columns: auto min-content;
    }
}

@media (min-width: 768px) {
    .button-stack {
        width: 100% !important;
        grid-template-columns: 1fr 1fr;
    }
    .input-with-verify-field {
        display: inline-grid;
        grid-template-columns: auto min-content;
    }
}

@media (min-width: 1024px) {
    .button-stack {
        justify-content: start;
        grid-template-columns: auto auto;
        width: 38rem;
        Button {
            width: 15rem !important;
            gap: 2rem;
            white-space: nowrap;
        }
    }
    .input-with-verify-field {
        width: 38rem;
    }
}
</style>
