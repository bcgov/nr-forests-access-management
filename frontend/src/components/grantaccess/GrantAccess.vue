<script setup lang="ts">
import router from '@/router';
import { ErrorMessage, Field, Form as VeeForm } from 'vee-validate';
import { onMounted, ref } from 'vue';
import { number, object, string } from 'yup';

import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import RadioButton from 'primevue/radiobutton';
import ForestClientCard from './ForestClientCard.vue';
import UserIdentityCard from './UserIdentityCard.vue';

import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
selectedApplication,
selectedApplicationDisplayText,
} from '@/store/ApplicationState';
import {
FOREST_CLIENT_INPUT_MAX_LENGTH,
domainOptions,
getGrantAccessFormData,
grantAccessFormData,
resetGrantAccessFormData,
setGrantAccessFormData,
} from '@/store/GrantAccessDataState';

import {
FamForestClientStatusType,
type FamApplicationRole,
type FamForestClient,
type IdimProxyIdirInfo
} from 'fam-api';

const defaultFormData = {
    domain: domainOptions.IDIR,
    userId: '',
    forestClientNumber: '',
    role_id: null as number | null,
};
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))); // clone default input
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
                    .required('Forest Client number is required')
                    .min(8, 'Forest Client ID must be 8 characters long'),
        })
        .nullable(),
});
const loading = ref<boolean>(false);
let applicationRoleOptions: FamApplicationRole[]
let forestClientData: FamForestClient[] | null
let verifiedUserIdentity: IdimProxyIdirInfo | null

const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const forestClientApi = apiServiceFactory.getForestClientApi();
const idirBceidProxyApi = apiServiceFactory.getIdirBceidProxyApi();

onMounted(async () => {
    try {
        applicationRoleOptions = (
            await applicationsApi.getFamApplicationRoles(
                selectedApplication.value?.application_id as number
            )
        ).data as FamApplicationRole[];

        if (grantAccessFormData.value) {
            formData.value = getGrantAccessFormData();
        } else {
            resetForm();
        }
    } catch (error: unknown) {
        router.push('/dashboard');
        return Promise.reject(error);
    }
});

const isIdirDomainSelected = () => {
    return formData.value.domain === domainOptions.IDIR
}

function userDomainChange() {
    resetVerifiedUserIdentity();
    formData.value.userId = '';
}

const getSelectedRole = (): FamApplicationRole | undefined => {
    return applicationRoleOptions?.find(
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

function forestClientCheckOnlyDigit(evt: KeyboardEvent) {
    if (isNaN(parseInt(evt.key))) {
        evt.preventDefault();
    }
}

function resetVerifiedUserIdentity() {
    verifiedUserIdentity = null
}

function resetForestClientNumberData() {
    forestClientData = null;
    formData.value.forestClientNumber = '';
}

function resetForm() {
    resetGrantAccessFormData();
    formData.value = defaultFormData;
}

function cancelForm() {
    resetForm();
    router.push('/dashboard');
}

async function verifyIdentity(userId: string, domain: string) {
    if (domain == domainOptions.BCEID) return; // IDIR search currently, no BCeID yet.

    loading.value = true;
    try {
        verifiedUserIdentity = (
            await idirBceidProxyApi.idirSearch(userId)
        ).data;
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
        loading.value = false;
    }
}

async function verifyForestClientNumber(forestClientNumber: string) {
    loading.value = true;
    try {
        forestClientData = (
            await forestClientApi.search(forestClientNumber)
        ).data;
    } catch (err: any) {
        return Promise.reject(err);
    } finally {
        loading.value = false;
    }
}

/*
Two verifications are cunnretly in place: userId and forestClientNumber.
*/
function areVerificationsPassed() {
    return (
        // userId verification.
        !isIdirDomainSelected() ||
        (
            isIdirDomainSelected() && verifiedUserIdentity?.found
        )
    ) &&
    (
        // forestClientNumber verification
        !isAbstractRoleSelected() ||
        (
            isAbstractRoleSelected() &&
            forestClientData?.[0]?.status?.status_code == FamForestClientStatusType.A
        )
    )
}

function toSummary() {
    setGrantAccessFormData(formData.value);
    router.push('/summary');
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
                <form
                    id="grantAccessForm"
                    class="form-container"
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
                                        :checked="isIdirDomainSelected()"
                                        inputId="idirSelect"
                                        name="domainRadioOptions"
                                        :value="domainOptions.IDIR"
                                        @change="userDomainChange()"
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
                                        inputId="becidSelect"
                                        name="domainRadioOptions"
                                        :value="domainOptions.BCEID"
                                        @change="userDomainChange()"
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

                            <!-- show Verify button only if (all applied):
                                * domain is IDIR (for now, BCeID is not availabe for verify yet)
                                * userId field is entered.
                                * userId entered does not contains basic validation errors.
                            -->
                            <div class="col-md-2"
                                v-if="
                                    formData.domain === domainOptions.IDIR &&
                                    formData.userId &&
                                    errors.userId == undefined
                                "
                                >
                                <Button
                                    class="button p-button-tertiary p-button-outlined"
                                    @click="
                                        verifyIdentity(formData.userId, formData.domain)
                                    "
                                    :disabled="loading"
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

                    <div class="row" v-if="verifiedUserIdentity">
                        <div class="form-group col-md-5 px-0">
                            <UserIdentityCard
                                :userIdentity="verifiedUserIdentity"
                            ></UserIdentityCard>
                        </div>
                    </div>

                    <div class="form-group col-md-3 px-0">
                        <label for="roleSelect" class="control-label px-0"
                            >Assign a role
                            {{ formData.userId ? 'to ' + formData.userId : ''
                            }}<span class="text-danger"> *</span></label
                        >
                        <Field
                            id="roleSelect"
                            class="form-select"
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
                                class="application-dropdown w-100"
                                v-bind="field.value"
                                @update:modelValue="handleChange"
                                @change="resetForestClientNumberData()"
                                :class="{ 'is-invalid': errors.role_id }"
                            >
                            </Dropdown>
                        </Field>
                        <ErrorMessage class="invalid-feedback" name="role_id" />
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
                                        v-on:keypress="
                                            forestClientCheckOnlyDigit($event)
                                        "
                                        @input="resetForestClientNumberData()"
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
                                        verifyForestClientNumber(
                                            formData.forestClientNumber as string
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
                    <div class="row" v-if="forestClientData">
                        <div class="form-group col-md-5 px-0">
                            <ForestClientCard
                                :text="forestClientData?.[0]?.client_name"
                                :status="forestClientData?.[0]?.status"
                            ></ForestClientCard>
                        </div>
                    </div>
                    <div
                        class="row gy-3 my-0"
                        v-if="meta.valid && areVerificationsPassed()"
                    >
                        <div class="col-auto px-0">
                            <Button
                                type="button"
                                id="grantAccessSubmit"
                                class="mb-3 button p-button"
                                label="Next"
                                @click="toSummary()"
                            ></Button>
                            <Button
                                class="m-3 button"
                                outlined
                                label="Cancel"
                                @click="cancelForm()"
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
