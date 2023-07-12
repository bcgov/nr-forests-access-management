<script setup inherit-attrs="false" lang="ts">
import type { useErrorDialog } from '@/store/ApplicationState';
import Dialog from 'primevue/dialog';
import { ref } from "vue";

defineProps<{
    header: string,
    textFirst: string,
    textSecond: string
}>()

</script>

<template>
        <Dialog modal :header="header.toUpperCase()" :style="{ width: '50vw' }" class="modal-dialog" >
            <p>{{ textFirst }}</p>
            <p>{{ textSecond }}</p>
        </Dialog>
</template>


<style scoped>
</style>
