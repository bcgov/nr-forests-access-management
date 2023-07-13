<script setup inherit-attrs="false" lang="ts">
import Dialog from 'primevue/dialog';

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
