<script setup lang="ts">
import PageTitle from '@/components/common/PageTitle.vue';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import { selectedApplication } from '@/store/ApplicationState';
import type {
    FamApplicationRole,
    FamForestClient,
    FamUserRoleAssignmentCreate,
} from 'fam-api';
import { onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';
import { Form as VeeForm, Field, ErrorMessage } from 'vee-validate';
import router from '@/router';
import { number, object, string } from 'yup';

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;
const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.
let applicationRoleOptions = ref<FamApplicationRole[]>([]);
let forestClient: FamForestClient[] | null = null;
let loading = ref<boolean>(false);
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
const userRoleAssignmentApi = apiServiceFactory.getUserRoleAssignmentApi();
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
                    .min(
                        8,
                        'Forest Client number must be at least 8 characters'
                    ),
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
            `User "${
                newUserRoleAssignmentPayload.user_name
            }" is granted with "${getSelectedRole()?.role_name}" access.`
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

function onRoleSelected(evt: any) {
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

function forestClientNumberChange() {
    invalidForestClient.value = true;
    forestClient = null;
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
    <PageTitle :displaySelectedApplication="true"></PageTitle>
    <VeeForm
        ref="form"
        v-slot="{ handleSubmit, errors, meta }"
        :validation-schema="schema"
        as="div"
    >
        <div class="row"><h4>Login credentials</h4></div>

        <form
            id="grantAccessForm"
            class="form-container"
            @submit.prevent="handleSubmit($event, grantAccess)"
        >
            <div class="row">
                <div class="form-group col-md-3">
                    <label for="domainInput" class="control-label"
                        >Select user's credential</label
                    >
                    <div>
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
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="form-group col-md-3">
                    <label for="userIdInput" class="control-label"
                        >Type user's
                        {{ formData.domain === 'I' ? 'IDIR' : 'BCeID'
                        }}<span class="text-danger"> *</span></label
                    >
                    <Field
                        type="text"
                        id="userIdInput"
                        class="form-control"
                        name="userId"
                        maxlength="20"
                        placeholder="User's credential"
                        v-model="formData.userId"
                        :validateOnChange="true"
                        :class="{ 'is-invalid': errors.userId }"
                    />
                    <ErrorMessage class="invalid-feedback" name="userId" />
                </div>
            </div>

            <div class="row">
                <div class="form-group col-md-3">
                    <label for="roleSelect" class="control-label"
                        >Role<span class="text-danger"> *</span></label
                    >
                    <Field
                        id="roleSelect"
                        as="select"
                        class="form-select"
                        name="role_id"
                        aria-label="Role Select"
                        v-model="formData.role_id"
                        :class="{ 'is-invalid': errors.role_id }"
                        @change="onRoleSelected"
                    >
                        <option
                            v-for="role in applicationRoleOptions"
                            :key="role.role_id"
                            :value="role.role_id"
                        >
                            {{ role.role_name }}
                        </option>
                    </Field>
                    <ErrorMessage class="invalid-feedback" name="role_id" />
                </div>
            </div>
            <div v-if="isAbstractRoleSelected()">
                <div class="row mb-0">
                    <label for="forestClientInput" class="col-sm control-label"
                        >Forest Client
                        <span class="text-danger"> *</span></label
                    >
                </div>

                <div class="row mt-0">
                    <div class="col-md-3">
                        <Field
                            type="text"
                            name="forestClientNumber"
                            id="forestClientInput"
                            class="form-control"
                            :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH"
                            placeholder="Forest Client Id - 8 digits"
                            v-model="formData.forestClientNumber"
                            v-on:keypress="onlyDigit($event)"
                            v-bind:disabled="loading"
                            @input="forestClientNumberChange()"
                            :validateOnChange="true"
                            :class="{
                                'is-invalid': errors.forestClientNumber,
                            }"
                        />
                        <ErrorMessage
                            class="invalid-feedback"
                            name="forestClientNumber"
                        />
                    </div>
                    <div class="col-md-3">
                        <button
                            class="btn btn-outline-primary"
                            type="button"
                            @click="
                                getForestClientNumber(
                                    formData.forestClientNumber
                                )
                            "
                            v-bind:disabled="
                                formData.forestClientNumber?.length < 8 ||
                                loading
                            "
                        >
                            <div v-if="loading">
                                <!-- <b-spinner small></b-spinner> -->
                                Loading...
                            </div>
                            <div v-else>Verify ID</div>
                        </button>
                    </div>
                </div>
            </div>
            <div class="row" v-if="forestClient">
                <div class="form-group col-md-3">
                    <label class="col-sm control-label"
                        >Organization details:</label
                    >
                    <ForestClientCard
                        :text="forestClient?.[0]?.client_name"
                        :status="forestClient?.[0]?.status"
                    ></ForestClientCard>
                </div>
            </div>

            <div class="row gy-3">
                <div class="col-auto">
                    <button
                        type="submit"
                        id="grantAccessSubmit"
                        class="btn btn-primary mb-3"
                        :disabled="!meta.valid || invalidForestClient"
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
.text-danger {
    font-weight: normal;
}
</style>
