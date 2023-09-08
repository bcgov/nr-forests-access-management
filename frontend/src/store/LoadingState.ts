import { ref } from 'vue';

// Loading state indicator (true/false).
// It is being triggered when async http request happens (used by axios interceptors).
// Components can read this indicator but DON'T need to set the value as it is being
// taking care by axios interceptors.
const isLoading = ref<boolean>(false);

export default {
    isLoading,
};
