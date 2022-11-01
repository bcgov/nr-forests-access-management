<script setup lang="ts">
import { applicationsUserAdministers, selectedApplicationShortDisplayText } from '../services/ApplicationService'

enum Page {
  HOME = 'Home',
  SELECT_APP = 'SelectApp',
  MANAGE = 'Manage',
  GRANT = 'Grant'
}
defineProps<{
  activePage: string 
}>()
</script>

<template>
  <span>
  <template v-if="activePage == Page.HOME">  
  </template>
  <template v-else>
    <RouterLink to="/">Home</RouterLink> 
    <template v-if="activePage == Page.SELECT_APP">
      &rarr; Select Application
    </template>
    <template v-else>
      <template v-if="applicationsUserAdministers.length > 1">
        &rarr; <RouterLink to="/application">Select Application</RouterLink> 
      </template>
      <template v-if="activePage == Page.MANAGE">
        &rarr; Manage Access: {{selectedApplicationShortDisplayText}}
      </template>
      <template v-else>
        &rarr; <RouterLink to="/manage">Manage Access</RouterLink> 
        <template v-if="activePage == Page.GRANT">
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
