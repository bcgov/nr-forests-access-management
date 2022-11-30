<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { useToast } from 'vue-toastification';

const domainOptions = {IDIR: 'I', BCEID: 'B'}

const formData = {
  domain: domainOptions.BCEID,
  userId: null,
  forestClientNumber: null,
  roleId: null
}

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
            v-model="formData.roleId">
            <option selected>Select A Role</option>
            <option value="fom_submitter">FOM Submitter</option>
            <option value="fom_reviewer">FOM Reviewer</option>
          </select>
        </div>
      </div>

      <div class="row">
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
            @click="save(true)">
            Grant Access
          </button>
        </div>
      </div>

    </form>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
