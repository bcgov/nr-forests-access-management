<script setup lang="ts">
import { formatUserNameAndId } from "@/utils/UserUtils";
import DotMarkIcon from "@carbon/icons-vue/es/dot-mark/16";
import { type FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api/model";

/**
 * A template for notification content on failed permission grants to regular users.
 */

const props = defineProps<{
    assignments: FamUserRoleAssignmentCreateRes[];
    applicationName: string | null;
}>();

const headerText = `Failed to send email for permissions granted in ${props.applicationName ?? "this application"}. Please contact users:`;

</script>

<template>
    <div class="failed-permission-content">
        <div class="notification-header">
            {{ headerText }}
        </div>

        <ul class="notification-list">
            <li
                v-for="assignment in props.assignments"
                :key="assignment.detail.user_id"
                class="notification-list-item"
            >
                <DotMarkIcon class="dot-mark-icon" />
                <span>
                    {{
                        formatUserNameAndId(
                            assignment.detail.user.user_name,
                            assignment.detail.user.first_name,
                            assignment.detail.user.last_name
                        )
                    }} - {{ assignment.detail.user.email }}
                </span>
            </li>
        </ul>
    </div>
</template>

<style scoped lang="scss">
.failed-permission-content {
    .notification-header {
        margin-bottom: 0.75rem;
        font-weight: 400;
        line-height: 1.5;
    }

    .notification-list {
        list-style-type: none;
        padding: 0;
        margin: 0;

        .notification-list-item {
            position: relative;
            line-height: 1.5;


            &::before {
                content: none;
            }

            .dot-mark-icon {
                margin-right: 0.5rem;
                width: 0.5em;
                height: 0.5em;
                fill: #212121;
            }

            &:last-child {
                margin-bottom: 0;
            }
        }
    }
}
</style>
