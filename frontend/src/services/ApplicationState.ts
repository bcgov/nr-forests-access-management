import type { FamApplication } from 'fam-api'
import { computed, ref } from 'vue'

// The applications the user has access to administer
export const applicationsUserAdministers = ref<FamApplication[]>([])

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication>()

export const isApplicationSelected = computed( () => {
    return selectedApplication.value != undefined
  })

export const selectedApplicationShortDisplayText = computed( () => {
if (selectedApplication.value) {
    return `${selectedApplication.value.application_name.toUpperCase()}`
}
else {
    return ""
}
})

export const selectedApplicationDisplayText = computed( () => {
    if (selectedApplication.value) {
      return `${selectedApplication.value.application_description}`
    }
    else {
      return ""
    }
  })
