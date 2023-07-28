import { reactive } from "vue"

export const useNotificationMessage = reactive({
    notificationMsg: '',
    isNotificationVisible: false,
})

export const useErrorDialog = reactive({
    isErrorVisible: false,
})