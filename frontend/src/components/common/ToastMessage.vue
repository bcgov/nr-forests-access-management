<script setup lang="ts">
import Toast from 'primevue/toast';
import { IconSize } from '@/enum/IconEnum';
</script>

<template>
    <Toast group="tl" position="top-right" #icon>
        <Icon
            icon="error--filled"
            :size="IconSize.large"
            class="custom-carbon-icon-error--filled"
        />
    </Toast>
</template>
