<script setup lang="ts">
import { ref } from 'vue'
import { ApiService } from '@/services/ApiService';
import PageTitle from '@/components/PageTitle.vue';
import router from '@/router';
import { POSITION, useToast } from 'vue-toastification';

const apiService = new ApiService()

interface UserRoleAssignment {
  user_role_xref_id: number,
  user: {
    user_type: {
      code: string,
      description: string
    }
    user_name: string
  },
  role: {
    role_name: string
    role_type_code: string
    client_number?: {
      client_name: string,
      forest_client_number: string
    }
  }

}

const userRoleAssignments = ref<UserRoleAssignment[]>([])

// TODO: Eliminate test data
userRoleAssignments.value = [
    {
        "user_role_xref_id": 1,
        "user": {
          "user_type": {
            code: "I",
            description: "IDIR",
          },
          "user_name": "foo-test"
        },
        "role": {
            "role_name": "Reviewer",
            "role_type_code": "C"
        }
    },
    {
        "user_role_xref_id": 2,
        "user": {
          "user_type": {
            code: "B",
            description: "BCeID",
          },
          "user_name": "bar-test"
        },
        "role": {
            "role_name": "Submitter",
            "role_type_code": "A",
            "client_number": {
                "client_name": "acme forestry",
                "forest_client_number": "00009876"
            }
        }
    },
    {
        "user_role_xref_id": 3,
        "user": {
          "user_type": {
            code: "B",
            description: "BCeID",
          },
          "user_name": "longer-user-id"
        },
        "role": {
            "role_name": "Submitter",
            "role_type_code": "A",
            "client_number": {
                "client_name": "Long name of forestry company",
                "forest_client_number": "12345678"
            }
        }
    }

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

function tryDelete(assignment: UserRoleAssignment) {
  let msg = `"Delete access for user ${assignment.user.user_name} from role ${assignment.role.role_name}`
  if (assignment.role.client_number) {
    msg += ` for client ${assignment.role.client_number.forest_client_number}`
  }
  msg += '?'
  useToast().warning(msg, {

    // color: 'orange',
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
      <td v-if="assignment.role.client_number">{{assignment.role.client_number?.client_name}} - {{assignment.role.client_number?.forest_client_number}}</td>
      <td v-else></td>
      <td><button class="btn" @click="tryDelete(assignment)">Delete</button></td>
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
