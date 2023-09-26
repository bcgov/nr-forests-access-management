<script setup lang="ts">
import Badge from 'primevue/badge';
const props = defineProps({
    text: {
        type: String,
        required: true,
        default: '',
    }
});
</script>
<template>
    <div>
        <Badge
            severity='success'
            :value="props.text"
        />
    </div>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
