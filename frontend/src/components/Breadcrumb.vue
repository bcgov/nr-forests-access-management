<script setup lang="ts">
import { applicationsUserAdministers, selectedApplicationShortDisplayText } from '@/services/ApplicationState'

</script>

<template>
  <span>
  <template v-if="$router.currentRoute.value.path == '/'">  
  </template>
  <template v-else>
    <RouterLink to="/">Home</RouterLink> 
    <template v-if="$router.currentRoute.value.path == '/application'">
      &rarr; Select Application
    </template>
    <template v-else>
      <template v-if="applicationsUserAdministers.length > 1">
        &rarr; <RouterLink to="/application">Select Application</RouterLink> 
      </template>
      <template v-if="$router.currentRoute.value.path == '/manage'">
        &rarr; Manage Access: {{selectedApplicationShortDisplayText}}
      </template>
      <template v-else>
        &rarr; <RouterLink to="/manage">Manage Access</RouterLink> 
        <template v-if="$router.currentRoute.value.path == '/grant'">
          &rarr; Grant Access: {{selectedApplicationShortDisplayText}}
        </template>
        <template v-else>
          &rarr; ERROR SHOULD NOT REACH
        </template>
      </template>
    </template>
  </template>

  </span>

</template>
