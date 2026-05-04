<script setup lang="ts">
import type { SelectedUser } from "@/types/SelectUserType";
import { formatUserNameAndId } from "@/utils/UserUtils";
import CheckmarkOutline from "@carbon/icons-vue/es/checkmark--outline/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { computed } from "vue";

/**
 * This component is intended to display a table of selected users for the UserSearch component.
 * UserSearch component manages the state of selected users and passes them as to this component for display.
 * The state of selected users is synchronized to the consumer component of the UserSearch component.
 */

type SelectedUserTableRow = SelectedUser;

const props = defineProps<{
  users: readonly SelectedUserTableRow[];
  multiUserMode?: boolean;
}>();

const emit = defineEmits<{
  (e: "selected-user-deleted", userId: string): void;
}>();

const handleDeleteUser = (userId: string) => {
  emit("selected-user-deleted", userId);
};

const tableUsers = computed(() => [...props.users]);
const userCount = computed(() => props.users.length);
</script>

<template>
  <div>
    <div v-if="users.length > 0" class="user-id-card-table">
      <div class="verified-message-bar">
        <CheckmarkOutline class="verified-icon" />
        <span class="verified-message-text">Verified user information</span>
      </div>
      <DataTable :value="tableUsers" stripedRows class="user-table">
        <Column field="userId" header="Username" />
        <Column header="Full Name">
          <template #body="{ data }">
            {{ formatUserNameAndId(null, data.firstName, data.lastName) }}
          </template>
        </Column>
        <Column field="email" header="Email" />
        <Column header="" class="action-col">
          <template #body="{ data }">
            <button class="btn btn-icon" title="Delete user" @click="handleDeleteUser(data.userId)">
              <TrashIcon />
            </button>
          </template>
        </Column>
      </DataTable>
    </div>
    <div v-if="multiUserMode && users.length > 0" class="user-bulk-message-bar">
      <span>
        <b>{{ userCount }} user{{ userCount > 1 ? 's' : '' }}</b>
        &nbsp;will receive the same permissions configured below
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.user-bulk-message-bar {
    margin-top: 0.7rem;
    border: 1px solid colors.$blue-10;
    background: #EFF6FF;
    color: colors.$blue-80;
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-size: 14px;
    font-weight: 400;
    display: flex;
    align-items: center;
    min-height: 38px;
    b {
        font-weight: 700;
    }
}

.user-id-card-table {
    margin-top: 2rem;
    .verified-message-bar {
        height: 38px;
        background: #F0FDF4;
        border: 1px solid colors.$green-10;
        display: flex;
        align-items: center;
        padding: 0 1rem;
        border-radius: 4px;
        margin-bottom: 0.7rem;
        font-weight: 400;
        font-style: normal;
        font-size: 14px;
        color: colors.$green-80;
        .verified-icon {
            margin-right: 0.75rem;
            width: 20px;
            height: 20px;
            stroke: colors.$green-80;
        }
        .verified-message-text {
            display: inline-block;
            vertical-align: middle;
            color: colors.$green-80;
        }
    }
    .user-table {
        width: 100%;
        .action-col {
            width: 48px;
            text-align: center;
        }
        .btn.btn-icon {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.25rem;
            display: flex;
            align-items: center;
            svg {
                width: 1rem;
                height: 1rem;
                color: inherit;
            }
        }
    }
}
</style>
