<template>
    <div class="root">
        <form id="grantAccessForm" class="form-container" @submit.prevent="grantAccess">
            <div class="row">
                <div class="form-group col-md-3">
                    <label for="domainInput" class="control-label">Domain</label>
                    <div>
                        <div class="form-check form-check-inline">
                            <input type="radio" id="becidSelect" name="domainRadioOptions" class="form-check-input"
                                :value="domainOptions.BCEID" v-model="formData.domain"
                                :checked="(formData.domain === domainOptions.BCEID)">
                            <label class="form-check-label" for="becidSelect">BCeID</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input type="radio" id="idirSelect" name="domainRadioOptions" class="form-check-input"
                                :value="domainOptions.IDIR" v-model="formData.domain"
                                :checked="(formData.domain === domainOptions.IDIR)">
                            <label class="form-check-label" for="idirSelect">IDIR</label>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="userIdInput" class="form-label">User Id</label><span class="text-danger">*</span>
                        <input type="text" id="userIdInput" class="form-control" name="userId" maxlength="20"
                            placeholder="User's Id"
                            :class="v$.userId.$dirty ? v$.userId.$invalid ? 'is-invalid' : 'is-valid' : null"
                            v-model="formData.userId" @blur.native="v$.userId.$touch()">
                        <div class="text-danger" v-for="error of v$.userId.$errors" :key="error.$uid">
                            <small>{{ error.$message }}</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-5">
                    <div class="form-group">

                        <label for="roleSelect" class="control-label">Role</label><span class="text-danger">*</span>
                        <select id="roleSelect" name="role" class="form-select" aria-label="Role Select"
                            v-model="formData.role"
                            :class="v$.role.$dirty ? v$.role.$invalid ? 'is-invalid' : 'is-valid' : null"
                            @change.native="v$.role.$touch()" @blur.native="v$.role.$touch()">
                            <option v-for="role in applicationRoleOptions" :value="role">{{ role.role_name }}</option>
                        </select>
                        <div class="text-danger" v-for="error of v$.role.$errors" :key="error.$uid">
                            <small>{{ error.$message }}</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row" v-if="formData.role?.role_name == 'A'">
                <div class="form-group col-md-3">
                    <label for="forestClientInput" class="control-label">Forest Client</label>
                    <input type="text" id="forestClientInput" class="form-control"
                        :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH" placeholder="Forest Client Id - 8 digits"
                        v-model="formData.forestClientNumber" v-on:keypress="onlyDigit($event)">
                </div>
            </div>

            <div class="row gy-3">
                <div class="col-auto">
                    <button type="submit" id="grantAccessSubmit" class="btn btn-primary mb-3"
                        :disabled="!v$.$anyDirty || v$.$invalid">
                        Grant Access
                    </button>
                </div>
            </div>
        </form>
    </div>
</template>

<script lang="ts">
import { ApiService, type ApplicationRoleResponse, type GrantUserRoleRequest } from '@/services/ApiService';
import { selectedApplication } from '@/services/ApplicationState';
import { ref } from 'vue';
import { useToast } from 'vue-toastification';

import { reactive } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, minLength, maxLength } from '@vuelidate/validators';
import type { button } from 'aws-amplify';

export default {
    setup() {
        const FOREST_CLIENT_INPUT_MAX_LENGTH = 8;
        const domainOptions = { IDIR: 'I', BCEID: 'B' }; // TODO, load it from backend when backend has the endpoint.

        const apiService = new ApiService();

        const defaultFormData = {
            domain: domainOptions.BCEID,
            userId: null,
            forestClientNumber: null,
            role: null as unknown as ApplicationRoleResponse
        };

        const formData = reactive({ ...defaultFormData });
        const rules = {
            domain: {},
            userId: { required, minLength: minLength(3), maxLength: maxLength(20) },
            role: { required },
            forestClientNumber: {},
        };

        const initialState = {
            name: "",
            lastName: "",
            email: ""
        };

        function resetForm() {
            Object.assign(formData, defaultFormData);
        };

        const v$ = useVuelidate(rules, formData);

        return { formData, v$, domainOptions, apiService, FOREST_CLIENT_INPUT_MAX_LENGTH, defaultFormData, resetForm }
    },
    data() {
        return { applicationRoleOptions: ref<ApplicationRoleResponse[]>([]), buttonDisabled: true }
    },
    computed: {
        onBlur() {
            this.v$.$validate();
            if (this.v$.$errors) this.buttonDisabled = true;
            else this.buttonDisabled = false;
        }
    },
    methods: {
        onlyDigit(evt: KeyboardEvent) {
            if (isNaN(parseInt(evt.key))) {
                evt.preventDefault();
            }
        },

        async grantAccess() {
            this.v$.$validate();
            if (this.v$.$error) return;
            const toast = useToast();
            const grantAccessRequest = this.toRequest(this.formData);
            try {
                await this.apiService.grantUserRole(grantAccessRequest);
                toast.success(`User "${grantAccessRequest.user_name}" is granted with "${this.formData?.role.role_name}" access.`);
                this.resetForm();
                this.v$.$reset();
            }
            catch (err: any) {
                useToast().error(`Grant Access failed due to an error. Please try again.If the error persists then contact support.\nMessage: ${err.response.data?.detail}`);
                console.error("err: ", err);
            }
        },

        toRequest(formData: any) {
            const request = {
                user_name: formData.userId,
                user_type_code: formData.domain,
                role_id: formData.role.role_id,
                ...(formData.forestClientNumber ?
                    { forest_client_number: formData.forestClientNumber.padStart(this.FOREST_CLIENT_INPUT_MAX_LENGTH, '0') }
                    : {})
            } as GrantUserRoleRequest;

            return request;
        }
    },
    async mounted() {
        this.applicationRoleOptions = await this.apiService.getApplicationRoles(
            selectedApplication?.value?.application_id
        ) as ApplicationRoleResponse[];
    }
}

</script>

<style scoped>

</style>