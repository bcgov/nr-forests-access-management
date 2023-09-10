import { ref } from 'vue';

/*
    Loading state indicator (true/false). For this Vue app axios instance.
    It is being triggered when async http request happens (used by app's axios interceptors).
    Components can read this indicator but *-DON'T-* need to set the value since it is being
    taken care by axios interceptors.

    If http is being triggered by third-party libraries, loading will need to be manually 
    set (not part of app's axios instance).
*/
const isLoading = ref<boolean>(false);

export default {
    isLoading,
};
