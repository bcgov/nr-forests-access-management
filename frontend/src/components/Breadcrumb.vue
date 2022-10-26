<script setup lang="ts">
import { selectedApplicationShortDisplayText } from '../services/ApplicationService'

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
    <RouterLink to="/">Home</RouterLink> &rarr; 
    <template v-if="activePage == Page.SELECT_APP">
      Select Application
    </template>
    <template v-else>
      <RouterLink to="/application">Select Application</RouterLink> &rarr; 
      <template v-if="activePage == Page.MANAGE">
        Manage Access: {{selectedApplicationShortDisplayText}}
      </template>
      <template v-else>
        <RouterLink to="/manage">Manage Access</RouterLink> &rarr;
        <template v-if="activePage == Page.GRANT">
          Grant Access: {{selectedApplicationShortDisplayText}}
        </template>
        <template v-else>
          ERROR SHOULD NOT REACH
        </template>
      </template>
    </template>
  </template>

  </span>

</template>

<style scoped>
</style>
