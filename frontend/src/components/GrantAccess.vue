<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiService, type ApplicationRoleResponse, type GrantUserRoleRequest } from '@/services/ApiService';
import { selectedApplication } from '@/services/ApplicationState';
import { onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';

const FOREST_CLIENT_INPUT_MAX_LENGTH = 8
const domainOptions = {IDIR: 'I', BCEID: 'B'} // TODO, load it from backend when backend has the endpoint.
let applicationRoleOptions = ref<ApplicationRoleResponse[]>([])

const defaultFormData = {
  domain: domainOptions.BCEID,
  userId: null,
  forestClientNumber: null,
  role: null as unknown as ApplicationRoleResponse
}
const formData = ref(JSON.parse(JSON.stringify(defaultFormData))) // clone default input data.

const apiService = new ApiService()

onMounted(async () => {
  applicationRoleOptions.value = await apiService.getApplicationRoles(
    selectedApplication?.value?.application_id
  ) as ApplicationRoleResponse[]
})

function onlyDigit(evt: KeyboardEvent) {
  if (isNaN(parseInt(evt.key))) {
    evt.preventDefault()
  }
}

async function grantAccess() {
  const toast = useToast();
  const grantAccessRequest = toRequest(formData.value)
  try {
    await apiService.grantUserRole(grantAccessRequest)
    toast.success(`User "${grantAccessRequest.user_name}"" is granted with "${formData.value.role.role_name}" access.`)
    formData.value = JSON.parse(JSON.stringify(defaultFormData)) // clone default input data.
  }
  catch(err: any) {
    useToast().error(`Grant Access failed due to an error. Please try again.If the error persists then contact support.\nMessage: ${err.response.data?.detail}`)
    console.error("err: ", err)
  } 
}

function toRequest(formData: any) {
  const request = {
    user_name: formData.userId,
    user_type_code: formData.domain,
    role_id: formData.role.role_id,
    ...(formData.forestClientNumber? 
        {forest_client_number: formData.forestClientNumber.padStart(FOREST_CLIENT_INPUT_MAX_LENGTH, '0')}
        : {})
  } as GrantUserRoleRequest

  return request
}

</script>

<template>

    <PageTitle :displaySelectedApplication=true></PageTitle>
  
    <form id="grantAccessForm" 
      class="form-container"
      @submit.prevent="grantAccess">
      <div class="row">
        <div class="form-group col-md-3">
          <label for="domainInput" class="control-label">Domain</label>
          <div>
            <div class="form-check form-check-inline">
              <input type="radio"
                id="becidSelect" 
                name="domainRadioOptions"
                class="form-check-input"
                :value="domainOptions.BCEID" 
                v-model="formData.domain"
                :checked="(formData.domain === domainOptions.BCEID)">
              <label class="form-check-label" for="becidSelect">BCeID</label>
            </div>
            <div class="form-check form-check-inline">
              <input 
                type="radio" 
                id="idirSelect" 
                name="domainRadioOptions"
                class="form-check-input"  
                :value="domainOptions.IDIR"
                v-model="formData.domain"
                :checked="(formData.domain === domainOptions.IDIR)">
              <label class="form-check-label" for="idirSelect">IDIR</label>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="form-group col-md-3">
          <label for="userIdInput" class="control-label">User Id</label>
          <input type="text" 
            id="userIdInput" 
            class="form-control"
            name="userId"
            required
            maxlength="20"
            placeholder="User's Id"
            v-model="formData.userId">
        </div>
      </div>

      <div class="row">
        <div class="form-group col-md-5">
          <label for="roleSelect" class="control-label">Role</label>
          <select id="roleSelect"
            name="role"
            required
            class="form-select" 
            aria-label="Role Select"
            v-model="formData.role">
            <option 
              v-for="role in applicationRoleOptions" 
              :value="role">{{role.role_name}}</option>
          </select>
        </div>
      </div>

      <div class="row" v-if="formData.role?.role_type_code == 'A'">
        <div class="form-group col-md-3">
          <label for="forestClientInput" class="control-label">Forest Client</label>
          <input type="text"
            id="forestClientInput"
            class="form-control"
            required
            :maxlength="FOREST_CLIENT_INPUT_MAX_LENGTH"
            placeholder="Forest Client Id - 8 digits"
            v-model="formData.forestClientNumber"
            v-on:keypress="onlyDigit($event)">
        </div>
      </div>

      <div class="row gy-3">
        <div class="col-auto">
          <button type="submit"
            id="grantAccessSubmit"
            class="btn btn-primary mb-3"
            >
            Grant Access
          </button>
        </div>
      </div>

    </form>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
