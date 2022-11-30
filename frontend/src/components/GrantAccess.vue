<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiService, type ApplicationRoleResponse } from '@/services/ApiService';
import { selectedApplication } from '@/services/ApplicationState';
import { onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';

const domainOptions = {IDIR: 'I', BCEID: 'B'}
let applicationRoleOptions = ref<ApplicationRoleResponse[]>([])

const formData = ref({
  domain: domainOptions.BCEID,
  userId: null,
  forestClientNumber: null,
  role: null as unknown as ApplicationRoleResponse
})

const apiService = new ApiService()

onMounted(async () => {
  applicationRoleOptions.value = await apiService.getApplicationRoles(selectedApplication?.value?.application_id) as ApplicationRoleResponse[]
})

function onlyDigit(evt: KeyboardEvent) {
  if (isNaN(parseInt(evt.key))) {
    evt.preventDefault()
  }
}

function save(result: boolean) {
  const toast = useToast();
  if (result) {
    toast.success("Save successful")
  } else {
    toast.warning("Invalid selection.")
  }  
}
</script>

<template>

    <PageTitle />
  
    <form id="grantAccessForm" class="form-container">
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
            placeholder="User's Id"
            v-model="formData.userId">
        </div>
      </div>

      <div class="row">
        <div class="form-group col-md-5">
          <label for="roleSelect" class="control-label">Role</label>
          <select id="roleSelect"
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
            maxlength="8"
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
            @click="$event.preventDefault();save(true)">
            Grant Access
          </button>
        </div>
      </div>

    </form>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
