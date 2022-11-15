<script setup lang="ts">
    import router from '@/router'
    import authService from '@/services/AuthService'

    /**
     * This component is to deal with Auth callback.
     */

    authService.methods.handlePostLogin().then(data => {
        // If auth success from Cognito, route to '/about' temporarily
        router.push('/about')
    })

</script>

<template>

</template>
