<script setup lang="ts">
    import router from '@/router'
    import authService from '@/services/AuthService'

    /**
     * This component is to deal with Auth callback.
     */

    authService.methods.handlePostLogin().then(data => {
        router.push('/application')
    })

</script>

<template>

</template>
