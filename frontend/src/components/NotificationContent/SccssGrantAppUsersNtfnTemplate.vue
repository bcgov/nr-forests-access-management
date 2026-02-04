<script setup lang="ts">
import { EmailSendingStatus, type FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api/model";
import { formatUserNameAndId } from "@/utils/UserUtils";
import DotMarkIcon from "@carbon/icons-vue/es/dot-mark/16";

/**
 * A 'successGrantRegularUsersNotificationTemplate' for notification content on successful
 * permission grants to regular users.
 */

const props = defineProps<{
    successAssignments: FamUserRoleAssignmentCreateRes[];
    applicationName: string | null;
}>();

const headerText = `Permission added in ${props.applicationName ?? "this application"} to users:`;

const getEmailSuffix = (
    emailStatus?: EmailSendingStatus | null,
    email?: string | null
): string => {
    if (!emailStatus || !email) {
        return "";
    }
    if (EmailSendingStatus.SentToEmailServiceSuccess === emailStatus) {
        return ` and email sent to ${email}`;
    }
    return "";
};
</script>

<template>
    <div class="success-permission-content">
        <div class="notification-header">
            {{ headerText }}
        </div>

        <ul class="notification-list">
            <li
                v-for="assignment in props.successAssignments"
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
                    }}{{
                        getEmailSuffix(
                            assignment.email_sending_status,
                            assignment.detail.user.email
                        )
                    }}
                </span>
            </li>
        </ul>
    </div>
</template>

<style scoped lang="scss">
.success-permission-content {
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
