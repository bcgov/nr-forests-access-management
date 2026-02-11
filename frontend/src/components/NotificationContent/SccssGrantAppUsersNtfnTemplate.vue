<script setup lang="ts">
import { computed, ref } from "vue";
import { EmailSendingStatus, type FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api/model";
import { formatUserNameAndId } from "@/utils/UserUtils";
import CheckMarkIcon from "@carbon/icons-vue/es/checkmark--filled/20";
import DotMarkIcon from "@carbon/icons-vue/es/dot-mark/16";

/**
 * A template for notification content on successful permission grants to regular users.
 */

const props = defineProps<{
    assignments: FamUserRoleAssignmentCreateRes[];
    applicationName: string | null;
}>();

const headerText = `Permission added to the following users`;

const isExpanded = ref(false);

const showToggle = computed(() => props.assignments.length > 2);
const visibleAssignments = computed(() => {
    if (!showToggle.value || isExpanded.value) {
        return props.assignments;
    }
    return props.assignments.slice(0, 2);
});

const toggleExpanded = () => {
    isExpanded.value = !isExpanded.value;
};

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
        <CheckMarkIcon />
        <div class="notification-body">
            <div class="notification-header">
                <strong>Success</strong>: {{ headerText }}
            </div>

            <button
                v-if="showToggle && isExpanded"
                class="toggle-link"
                type="button"
                @click="toggleExpanded"
            >
                show less...
            </button>

            <ul class="notification-list">
                <li
                    v-for="assignment in visibleAssignments"
                    :key="assignment.detail!.user_id"
                    class="notification-list-item"
                >
                    <DotMarkIcon class="dot-mark-icon" />
                    <span>
                        {{
                            formatUserNameAndId(
                                assignment.detail!.user.user_name,
                                assignment.detail!.user.first_name,
                                assignment.detail!.user.last_name
                            )
                        }}{{
                            getEmailSuffix(
                                assignment.email_sending_status,
                                assignment.detail!.user.email
                            )
                        }}
                    </span>
                </li>
            </ul>

            <button
                v-if="showToggle && !isExpanded"
                class="toggle-link"
                type="button"
                @click="toggleExpanded"
            >
                show more...
            </button>
        </div>
    </div>
</template>

<style scoped lang="scss">
.success-permission-content {
    display: flex;
    align-items: flex-start;

    // Ensure icon stays sized and aligned
    > svg {
        flex-shrink: 0;
        margin-top: 0.15em;
    }

    .notification-body {
        flex: 1 1 0%;
    }

    .notification-header {
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

    .toggle-link {
        background: none;
        border: none;
        padding: 0;
        margin: 0 0 0.25rem;
        color: inherit;
        font-style: italic;
        text-decoration: underline;
        cursor: pointer;
    }
}
</style>
