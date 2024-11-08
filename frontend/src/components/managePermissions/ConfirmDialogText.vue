<script setup lang="ts">
import type { ConfirmTextType } from "./utils";

withDefaults(defineProps<ConfirmTextType>(), { customMsg: "access" });
</script>

<template>
    <p>
        Are you sure you want to remove
        <strong>{{ role }}</strong> {{ customMsg }} from
        <strong>{{ userName }}</strong> in <strong>{{ appName }}</strong
        >?
    </p>
</template>
