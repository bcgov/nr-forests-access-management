import { useToast } from "vue-toastification"
import axios, { type AxiosError } from "axios";

function onError(error: any, info: string) {
    console.error(`Error occurred: ${error.toString()}`)
    const toast = useToast();
    const genericErrorMsg = "An application error has occurred. Please try again. If the error persists contact support."

    // Axios Http instance error that we like to pop out additional toast message.
    if (axios.isAxiosError(error)) {
        const err = error as AxiosError
        const axiosResponse = err.response
        const status = axiosResponse?.status

        const e401_authenticationErrorMsg = "You are not logged in. Please log in."
        const e403_authorizationErrorMsg = "You do not have the necessary authorization for the requested action."
        const e409_conflictErrorMsg = `${axiosResponse?.data.detail}`

        if (!status) {
            toast.error(genericErrorMsg)
        }
        else if (status == 401) {
            toast.error(e401_authenticationErrorMsg)
        }
        else if (status == 403) {
            toast.error(e403_authorizationErrorMsg)
        }
        else if (status == 409) {
            toast.warning(e409_conflictErrorMsg)
        }
        return
    }

    toast.error(genericErrorMsg)
}

export default {
    onError
}