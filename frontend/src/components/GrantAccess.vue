<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { selectedApplication } from '@/services/ApplicationState';
import { useToast } from 'vue-toastification';

function save(result: boolean) {
  const toast = useToast();
  if (result) {
    toast.success("Save successful")
  } else {
    toast.warning("Invalid selection.")
  }  
}

function saveError() {
  useToast().error("Save failed due to an error. Please try again. If the error persists then contact support.")
}

function uncaughtError() {
  throw new Error("test uncaught error thrown from function")
}
</script>

<template>

    <PageTitle />
  
    <form id="grantAccessForm" class="form-container">
      <div class="row">
        <div class="form-group col-md-3">
          <label for="userIdInput" class="control-label">User Id</label>
          <input type="text" class="form-control" id="userIdInput" placeholder="User's Id">
        </div>
      </div>

      <div class="row">
        <div class="form-group col-md-3">
          <label for="domainInput" class="control-label">Domain</label>
          <div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="domainRadioOptions" id="becidSelect" value="option1">
              <label class="form-check-label" for="becidSelect">BCeID</label>
            </div>
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="domainRadioOptions" id="idirSelect" value="option2">
              <label class="form-check-label" for="idirSelect">IDIR</label>
            </div>
          </div>
        </div>
        <div></div>
      </div>

      <div class="row">
        <div class="form-group col-md-5">
          <label for="roleSelect" class="control-label">Role</label>
          <select class="form-select" id="roleSelect" aria-label="Role Select">
            <option selected>Select A Role</option>
            <option value="fom_submitter">FOM Submitter</option>
            <option value="fom_reviewer">FOM Reviewer</option>
          </select>
        </div>
      </div>

      <div class="row">
        <div class="form-group col-md-3">
          <label for="forestClientInput" class="control-label">Forest Client</label>
          <input type="number" class="form-control" id="forestClientInput" placeholder="Forest Client Id">
        </div>
      </div>

    </form>

    <!-- <p>Selection: {{selectedApplication}}</p> -->

    <br/>TODO<br/>
    <button @click="save(true)">Save</button>
    &nbsp;
    <button @click="save(false)">Validation failure</button>
    &nbsp;
    <button @click="saveError()">Save Error</button>
    &nbsp;
    <button @click="uncaughtError()">Uncaught Error</button>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
