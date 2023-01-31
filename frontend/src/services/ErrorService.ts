import { useToast } from "vue-toastification"
import type { AxiosError } from 'axios'

function onError(error: unknown, info: string) {
    const toast = useToast();
    const err = error as AxiosError

    console.log(`app.config.errorHandler error ${err} with info: ${info}`)
    if (err.response?.status == 401) {
      toast.error('Not logged in. Please log in.')
      return
    }
    if (err.response?.status == 403) {
      toast.error('You are not allowed to do that.')
      return
    }
    if (err.response?.status == 409) {
      toast.warning(`${err.response?.data.detail}`)
      return
    }
    toast.error('An application error has occurred. Please try again. If the error persists contact support.')
}

export default {
    onError
}