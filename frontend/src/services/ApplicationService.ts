import { computed, ref } from 'vue'

// These are the key properties for an Application returned by the back-end API
export interface Application {
    application_name: string;
    application_description: string;
    application_id: number;

}

// The applications the user has access to administer
export const applicationsUserAdministers = ref<Application[]>([])

// The application selected by the user to admin
export const selectedApplication = ref<Application>() 


export const isApplicationSelected = computed( () => {
    return selectedApplication.value == null
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
  