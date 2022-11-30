<script setup lang="ts">
import { ref } from 'vue'
import { ApiService } from '@/services/ApiService';
import PageTitle from '@/components/PageTitle.vue';
import router from '@/router';
import { useToast } from 'vue-toastification';

const apiService = new ApiService()

interface UserRoleAssignment {
    assignment_id: number;
    user_id: string;
    user_domain: string;
    role: string
    forest_client_number?: string;
}

const userRoleAssignments = ref<UserRoleAssignment[]>([])

// TODO: Eliminate test data
userRoleAssignments.value = [
  {
    assignment_id: 1,
    user_id: 'foo-test',
    user_domain: 'IDIR',
    role: 'Reviewer',
  },
  {
    assignment_id: 2,
    user_id: 'bar-test',
    user_domain: 'BCeID',
    role: 'Submitter',
    forest_client_number: '01234567'
  },
  {
    assignment_id: 3,
    user_id: 'long-user-name',
    user_domain: 'BC Services Card',
    role: 'long-role-name',
    forest_client_number: '00008765'
  },
]

// TODO: Need API
// userRoleAssignments.value = await apiService.getUserRoleAssignments(selectedApplication.value?.application_id)

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

  // TODO: Review this logic.

  if (userFilter.value != null) {
    if (!userRoleAssignment.user_id.toLocaleUpperCase().includes(userFilter.value.toLocaleUpperCase())) {
      return false
    }
  }

  if (roleFilter.value != null) {
    if (!userRoleAssignment.role.toLocaleUpperCase().includes(roleFilter.value.toLocaleUpperCase())) {
      return false
    }
  }

  if (forestClientFilter.value != null && forestClientFilter.value.length > 0) {
    if (userRoleAssignment.forest_client_number == null) {
      return false // If no forest client for the role then exclude this assignment when filtering by forest client
    } else if (!userRoleAssignment.forest_client_number.includes(forestClientFilter.value)) {
      return false
    }
  }
  return true
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

  <PageTitle />

  <!-- TODO: Bootstrap styling. -->
  <span>
    <button class="btn btn-info"  @click="router.push('/grant')">Grant Access</button>
  </span>
  <br/>
  <br/>
  <template v-if="userRoleAssignments.length > 0">
  <span><strong>Filter By:</strong></span>
  <span>
  User <input placeholder="user" v-model="userFilter" size="12"/></span>
  &nbsp;
  <span>Role <input placeholder="role" v-model="roleFilter" size="12"/></span>
  &nbsp;
  <span>Forest Client <input placeholder="client #" v-model="forestClientFilter" size="8"/></span>
  &nbsp;
  <span><strong>{{showingMessage()}}</strong></span>
  <table style="max-width: 800px;margin-top:10px" class="table table-sm table-striped" aria-describedby="User assignments to application roles.">
    <thead>
      <tr>
        <th scope="col">User</th>
        <th scope="col">Domain</th>
        <th scope="col">Role</th>
        <th scope="col">Forest Client</th>
      </tr>
    </thead>
    <tbody>
    <template v-for="assignment in userRoleAssignments">
    <tr v-if="filterIncludes(assignment)">
      <th scope="row">{{assignment.user_id}}</th>
      <td>{{assignment.user_domain}}</td>
      <td>{{assignment.role}}</td>
      <td>{{assignment.forest_client_number}}</td>
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
<button class="btn btn-info" @click="save(false)">Validation failure</button>
&nbsp;
<button class="btn btn-info" @click="saveError()">Save Error</button>
&nbsp;
<button class="btn btn-info" @click="uncaughtError()">Uncaught Error</button>

</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>
