<script setup lang="ts">
import { selectedApplicationDisplayText } from '@/store/ApplicationState';
const props = defineProps({
    role: {
        type: String,
        required: true
    },
    userName: {
        type: String,
        required: true
    }
});
</script>

<template>
    <p>
        Are you sure you want to remove
        <strong>{{ props.role }}</strong> access to
        <strong>{{ props.userName }}</strong> in
        <strong>{{ selectedApplicationDisplayText }}</strong>
    </p>
</template>

<style lang="scss">

</style>