<script setup lang="ts">
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import CheckmarkOutline from "@carbon/icons-vue/es/checkmark--outline/16";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import { formatUserNameAndId } from "@/utils/UserUtils";
import type { IdimProxyBceidInfoSchema } from "fam-app-acsctl-api";

const props = defineProps<{
    userList: IdimProxyBceidInfoSchema[];
    multiUserMode?: boolean;
}>();

const emit = defineEmits(["deleteUser"]);
const handleDelete = (userId: string) => emit("deleteUser", userId);
</script>

<template>
    <div class="user-id-card-table">
        <div class="verified-message-bar">
            <CheckmarkOutline class="verified-icon" />
            <span class="verified-message-text">Verified user information</span>
        </div>
        <DataTable :value="props.userList" stripedRows class="user-table">
            <Column field="userId" header="Username" />
            <Column header="Full Name">
                <template #body="{ data }">
                    {{ formatUserNameAndId(null, data.firstName, data.lastName) }}
                </template>
            </Column>
            <Column field="email" header="Email" />
            <Column v-if="props.multiUserMode" header="" class="action-col">
                <template #body="{ data }">
                    <button class="btn btn-icon" title="Delete user" @click="handleDelete(data.userId)">
                        <TrashIcon />
                    </button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<style lang="scss">
.user-id-card-table {
    margin-top: 2rem;
    .verified-message-bar {
        height: 38px;
        background: #F0FDF4;
        border: 1px solid #B9F8CF;
        display: flex;
        align-items: center;
        padding: 0 1rem;
        border-radius: 4px;
        margin-bottom: 0.7rem;
        font-family: 'BC Sans', 'Noto Sans', Arial, sans-serif;
        font-weight: 400;
        font-style: normal;
        font-size: 14px;
        color: #1a6333;
        .verified-icon {
            margin-right: 0.75rem;
            width: 20px;
            height: 20px;
            stroke: #008236;
        }
        .verified-message-text {
            display: inline-block;
            vertical-align: middle;
            color:#0D542B
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
