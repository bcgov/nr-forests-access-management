<script setup lang="ts">
import { onMounted, ref } from 'vue'
import router from '@/router';
import { useToast } from 'vue-toastification';
import { ApiService, type UserRoleAssignment } from '@/services/ApiService';
import PageTitle from '@/components/PageTitle.vue';
import { isApplicationSelected, selectedApplication } from '@/services/ApplicationState';

// import { $vfm } from 'vue-final-modal';
import Dialog from '@/components/Dialog/Dialog.vue'

import { $vfm } from 'vue-final-modal'


const apiService = new ApiService();

// Initialize as null to indicate not yet loaded.
const userRoleAssignments = ref<UserRoleAssignment[]>()

onMounted(async () => {
  if (selectedApplication.value != null) {
    const list = await apiService.getUserRoleAssignments(selectedApplication.value!.application_id)
    userRoleAssignments.value = list.sort((first,second) => {
      const nameCompare = first.user.user_name.localeCompare(second.user.user_name);
      if (nameCompare != 0) return nameCompare
      const roleCompare = first.role.role_name.localeCompare(second.role.role_name)
      return roleCompare
    })
  } else {
    // No application selected so redirect to select application screen
    // Unsure if this actually works...
    router.push("/application")
  }
})

const userFilter = ref<string>()
const roleFilter = ref<string>()
const forestClientFilter = ref<string>()

function showingMessage(): string {
  if (userRoleAssignments.value == null) {
    return ""
  }
  let visible = 0;
  userRoleAssignments.value.forEach(assignment => {
    if (filterIncludes(assignment)) {
      visible++
    }
  })

  return "Showing " + visible + " of " + userRoleAssignments.value.length + " records"
}

function filterIncludes(userRoleAssignment: UserRoleAssignment): boolean {

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
  let msg = `Delete access for user ${assignment.user.user_name} from role ${assignment.role.role_name}`
  if (assignment.role.client_number) {
    msg += ` for client ${assignment.role.client_number.forest_client_number}`
  }
  msg += '?'

  $vfm.show({
    component: Dialog,
    bind: {
      title: 'Are you sure?',
      message: msg,
      confirmText: 'Yes, delete'
    },
    on: {
      confirm() {
        // Deletion confirmed.
        try {
          apiService.deleteUserRoleAssignment(assignment.user_role_xref_id)

          userRoleAssignments.value = userRoleAssignments.value!.filter(a => {
            return !(a.user_role_xref_id == assignment.user_role_xref_id);
          })
          useToast().success(`Access deleted for user ${assignment.user.user_name}.`);
        } finally {
          $vfm.hideAll();
        }
      },
    }
  })
}

</script>

<template>
  <div>
    <PageTitle :displaySelectedApplication=true></PageTitle>

    <span>
      <button class="btn btn-info" @click="router.push('/grant')">Grant Access</button>
    </span>
    <br />
    <br />
    <template v-if="userRoleAssignments != null && userRoleAssignments.length > 0">
      <span><strong>Filter By:</strong></span>
      <span>
        Username <input placeholder="username" v-model="userFilter" size="12" /></span>
      &nbsp;
      <span>Role <input placeholder="role" v-model="roleFilter" size="12" /></span>
      &nbsp;
      <span>Forest Client <input placeholder="forest client" v-model="forestClientFilter" size="8" /></span>
      &nbsp;
      <span>{{ showingMessage() }}</span>
      <table style="max-width: 900px;margin-top:10px" class="table table-sm table-striped table-hover"
        aria-describedby="User assignments to application roles.">
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
              <th scope="row">{{ assignment.user.user_name }}</th>
              <td>{{ assignment.user.user_type.description }}</td>
              <td>{{ assignment.role.role_name }}</td>
              <td v-if="assignment.role.client_number">{{ assignment.role.client_number?.forest_client_number }}</td>
              <td v-else></td>
              <td><button class="btn btn-icon" @click="tryDelete(assignment)"><font-awesome-icon
                    icon="fa-regular fa-trash-can" /></button></td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>
    <template v-else-if="userRoleAssignments == null">
      Loading user role assignments...
    </template>
    <template v-else>
      No user role assignments found.
    </template>
  </div>

</template>

<style lang="scss" scoped>
  @import "@/assets/styles/styles.scss";
</style>
