<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiService, type UserRoleAssignment } from '@/services/ApiService';
import PageTitle from '@/components/PageTitle.vue';
import { DialogWrapper } from 'vue3-promise-dialog';
import router from '@/router';
import { POSITION, useToast } from 'vue-toastification';
import { selectedApplication } from '@/services/ApplicationState';

const apiService = new ApiService()

const userRoleAssignments = ref<UserRoleAssignment[]>([])

onMounted(async () => {
  if (selectedApplication.value) {
    userRoleAssignments.value = await apiService.getUserRoleAssignments(selectedApplication.value?.application_id)
    // TODO: Sort results by username, role, etc.
  } else {
    // TODO: Redirect to select application screen?
  }
})


const userFilter = ref<string>()
const roleFilter = ref<string>()
const forestClientFilter = ref<string>()

function showingMessage(): string {
  let visible = 0;
  userRoleAssignments.value.forEach(assignment => {
    if (filterIncludes(assignment)) {
      visible++
    }
  })

  return "Showing " + visible + " of " + userRoleAssignments.value.length + " records"
}

function filterIncludes(userRoleAssignment: UserRoleAssignment):boolean {

  // TODO: Review/test this logic.

  if (userFilter.value != null) {
    if (!userRoleAssignment.user.user_name.toLocaleUpperCase().includes(userFilter.value.toLocaleUpperCase())) {
      return false
    }
  }

  if (roleFilter.value != null) {
    if (!userRoleAssignment.role.role_name.toLocaleUpperCase().includes(roleFilter.value.toLocaleUpperCase())) {
      return false
    }
  }

  if (forestClientFilter.value != null && forestClientFilter.value.length > 0) {
    if (userRoleAssignment.role.client_number == null) {
      return false // If no forest client for the role then exclude this assignment when filtering by forest client
    } else if (!(
      userRoleAssignment.role.client_number.forest_client_number.includes(forestClientFilter.value) ||
      userRoleAssignment.role.client_number.client_name.toLocaleUpperCase().includes(forestClientFilter.value.toLocaleUpperCase())
      )) {
      return false
    }
  }
  return true
}

async function tryDelete(assignment: UserRoleAssignment) {
  let msg = `"Delete access for user ${assignment.user.user_name} from role ${assignment.role.role_name}`
  if (assignment.role.client_number) {
    msg += ` for client ${assignment.role.client_number.forest_client_number}`
  }
  msg += '?'
  /*
  useToast().warning(msg, {

    position: POSITION.TOP_CENTER,
    timeout: false,

    pauseOnFocusLoss: true,
    pauseOnHover: true,

    // TODO: Add question mark icon https://fontawesome.com/docs/web/use-with/vue/add-icons
    // E.g. icon: 'fas fa-rocket'
    icon: true,

    // TODO: Add yes/no actions using custom close button?
    closeButton: "button",

  })
*/
  // TODO: This confirmation dialog is ugly. Different from the demo, not sure why...
  // confirmation dialog only displays properly if invoked in app setup.
  if (await confirm(msg) ) {
    // Deletion confirmed.
    // TODO: Call API

    // Remove item deleted from list.
    userRoleAssignments.value = userRoleAssignments.value.filter(a => {
      return !(a.user_role_xref_id == assignment.user_role_xref_id)
    })

    useToast().success(`Access deleted for user ${assignment.user.user_name}.`)
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

function saveError() {
  useToast().error("Save failed due to an error. Please try again. If the error persists then contact support.")
}

function uncaughtError() {
  throw new Error("test uncaught error thrown from function")
}

</script>

<template>
  <div>

  <PageTitle :displaySelectedApplication=true></PageTitle>

  <!-- TODO: Bootstrap styling. -->
  <span>
    <button class="btn btn-info"  @click="router.push('/grant')">Grant Access</button>
  </span>
  <br/>
  <br/>
  <template v-if="userRoleAssignments.length > 0">
  <span><strong>Filter By:</strong></span>
  <span>
  Username <input placeholder="username" v-model="userFilter" size="12"/></span>
  &nbsp;
  <span>Role <input placeholder="role" v-model="roleFilter" size="12"/></span>
  &nbsp;
  <span>Forest Client <input placeholder="forest client" v-model="forestClientFilter" size="8"/></span>
  &nbsp;
  <span>{{showingMessage()}}</span>
  <table style="max-width: 900px;margin-top:10px" class="table table-sm table-striped table-hover" aria-describedby="User assignments to application roles.">
    <thead>
      <tr>
        <th scope="col">Username</th>
        <th scope="col">Domain</th>
        <th scope="col">Role</th>
        <th scope="col">Forest Client</th>
        <th scope="col"></th>
      </tr>
    </thead>
    <tbody>
    <template v-for="assignment in userRoleAssignments">
    <tr v-if="filterIncludes(assignment)">
      <th scope="row">{{assignment.user.user_name}}</th>
      <td>{{assignment.user.user_type.description}}</td>
      <td>{{assignment.role.role_name}}</td>
      <td v-if="assignment.role.client_number">{{assignment.role.client_number?.forest_client_number}}</td>
      <td v-else></td>
      <td><button class="btn btn-icon" @click="tryDelete(assignment)"><font-awesome-icon icon="fa-regular fa-trash-can" /></button></td>
    </tr>
    </template>
    </tbody>
  </table>

  </template>
  <template v-else>
    No user role assignments found.
  </template>
</div>
<br/>

<p>Demo of toast messages:</p>
<button class="btn btn-info" @click="save(true)">Save</button>
&nbsp;
<button class="btn btn-info" @click="save(false)">Validation failure</button>
&nbsp;
<button class="btn btn-info" @click="saveError()">Save Error</button>
&nbsp;
<button class="btn btn-info" @click="uncaughtError()">Uncaught Error</button>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
