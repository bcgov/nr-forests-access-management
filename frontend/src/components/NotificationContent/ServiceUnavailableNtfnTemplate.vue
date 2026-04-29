<script setup lang="ts">

import WarnIcon from "@carbon/icons-vue/es/warning--filled/16";

interface Props {
  message?: string | null;
}
const props = withDefaults(defineProps<Props>(), {
  message: "External service is unavailable. Please try again later.",
});

</script>

<template>
  <div class="forest-client-service-warning">
    <WarnIcon class="warning-icon" />
    <div class="notification-body">
      <div class="notification-header">
        <strong>Error</strong>: {{ props.message }}
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.forest-client-service-warning {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 0.5rem 0 1rem 0;
  padding: 0.5rem 1rem;
  border: 1px solid var(--support-error, #da1e28);
  border-left: 0.375rem solid var(--support-error, #da1e28);
  border-radius: 0.125rem;
  background-color: #fff1f1;
  color: var(--text-primary, #161616);

  .warning-icon {
    fill: var(--support-error, #da1e28);
    flex-shrink: 0;
    margin-top: 0.15rem;
  }

  .notification-body {
    flex: 1 1 0%;

    .notification-header {
      font-size: 0.875rem;
      font-weight: 400;
      line-height: 1.5;
    }
  }
}
</style>
