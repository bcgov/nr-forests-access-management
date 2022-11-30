<script setup lang="ts">
import { ref } from 'vue'
import router from '@/router';
import { selectedApplication, isApplicationSelected, selectedApplicationDisplayText } from '@/services/ApplicationState'

import { ApiService } from '@/services/ApiService';
import { useToast } from 'vue-toastification'

const apiService = new ApiService()

interface UserRoleAssignment {
    assignment_id: number;
    user_id: string;
    user_domain: string;
    role: string
    forest_client_number?: string;
}

const userRoleAssignments = ref<UserRoleAssignment[]>([])

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
  }

]
// TODO: Need API
// userRoleAssignments.value = await apiService.getUserRoleAssignments(selectedApplication.value?.application_id)

const userFilter = ref<string>()
const roleFilter = ref<string>()
const forestClientFilter = ref<string>()

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

</script>

<template>
  <div>

  <h1>Manage Access - {{selectedApplicationDisplayText}}</h1>

  <span>
    <button @click="router.push('/grant')">Grant Access</button>
  </span>
  <br/>
  <br/>
  <span><strong>Filter By:</strong></span>
  <span>
  User <input placeholder="user" v-model="userFilter" size="10"/>
  &nbsp;
  Role <input placeholder="role" v-model="roleFilter" size="10"/>
  &nbsp;
  Forest Client <input placeholder="client #" v-model="forestClientFilter" size="8"/>
  </span>

  <table class="table">
    <thead>
      <tr>
        <th scope="col">User</th>
        <th scope="col">Domain</th>
        <th scope="col">Role</th>
        <th scope="col">Forest Client</th>
      </tr>
    </thead>
    <template v-for="assignment in userRoleAssignments">
    <tr v-if="filterIncludes(assignment)">
      <td>{{assignment.user_id}}</td>
      <td>{{assignment.user_domain}}</td>
      <td>{{assignment.role}}</td>
      <td>{{assignment.forest_client_number}}</td>
    </tr>
    </template>
  </table>

</div>
</template>

<style scoped>

</style>
