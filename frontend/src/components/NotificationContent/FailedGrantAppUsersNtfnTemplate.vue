<script setup lang="ts">
import { mapAppUserGrantResponseByUserId } from "@/utils/ApiUtils";
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import type { AppPermissionQueryErrorType } from "@/views/AddAppPermission/utils";
import DotMarkIcon from "@carbon/icons-vue/es/dot-mark/16";
import MisuseIcon from "@carbon/icons-vue/es/misuse/20";
import { RoleType } from "fam-admin-mgmt-api/model";
import { EmailSendingStatus, type FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api/model";
import { computed, ref } from "vue";

/**
 * A template for notification content on failed permission grants to regular users.
 * props:
 * - assignments: An optional array of user role assignment responses.
 * - applicationName: The name of the application for which permissions were granted.
 * - requestErrorData: Optional error data related to the permission grant request.
 *
 * Note:
 * - Either asignments or requestErrorData should be provided to render meaningful content.
 */

const props = defineProps<{
    assignments?: FamUserRoleAssignmentCreateRes[];
    applicationName: string | null;
    requestErrorData?: AppPermissionQueryErrorType
}>();

if ((!props.assignments && !props.requestErrorData) || (props.assignments && props.requestErrorData)) {
    throw new Error("Programming Error: Either 'assignments' or 'requestErrorData' prop must be provided but not both.");
}
const PREVIEW_LIMIT = 2;

//--- Email seinding failure case setup
const headerText_failedEmailSending = `Failed to send email for permissions granted to the following users`;

// grouped by user ID and use first result per user for notification
const emailSendingErr_assignments = Array.from(
    mapAppUserGrantResponseByUserId(
        (props.assignments ?? []).filter(
            (a) => a.email_sending_status === EmailSendingStatus.SentToEmailServiceFailure
        )
    ).values()
).map((items) => items[0]);

const emailSendingErr_isExpanded = ref(false);
const emailSendingErr_showToggle = computed(() => emailSendingErr_assignments.length > 2);
const emailSendingErr_visibleAssignments = computed(() => {
    if (!emailSendingErr_showToggle.value || emailSendingErr_isExpanded.value) {
        return emailSendingErr_assignments;
    }
    return emailSendingErr_assignments.slice(0, 2);
});
const emailSendingErr_toggleExpanded = () => {
    emailSendingErr_isExpanded.value = !emailSendingErr_isExpanded.value;
};

//--- requestErrorData (general error case) setup
const reqErr_showAllUsers = ref(false);
const reqErr_showAllClients = ref(false);
const reqErr_roleName = props.requestErrorData?.formData.role?.display_name;
const isAbstractRole = props.requestErrorData?.formData.role?.type_code === RoleType.A;
const reqErr_users = props.requestErrorData?.formData.users ?? [];
const reqErr_forestClients = props.requestErrorData?.formData.forestClients ?? [];
const reqErr_visibleUsers = computed(() => reqErr_showAllUsers.value ? reqErr_users : reqErr_users.slice(0, PREVIEW_LIMIT));
const reqErr_remainingUsers = Math.max(reqErr_users.length - PREVIEW_LIMIT, 0);
const reqErr_visibleClients = computed(() => reqErr_showAllClients.value ? reqErr_forestClients : reqErr_forestClients.slice(0, PREVIEW_LIMIT));
const reqErr_remainingClients = Math.max(reqErr_forestClients.length - PREVIEW_LIMIT, 0);
</script>

<template>
    <template v-if="emailSendingErr_assignments && emailSendingErr_assignments.length > 0">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong> {{ headerText_failedEmailSending }}:
                </div>

                <button
                    v-if="emailSendingErr_showToggle && emailSendingErr_isExpanded"
                    class="toggle-link"
                    type="button"
                    @click="emailSendingErr_toggleExpanded"
                >
                    show less...
                </button>

                <ul class="notification-list user-list">
                    <li
                        v-for="assignment in emailSendingErr_visibleAssignments"
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
                            }} {{ assignment.detail.user.email ? ' - ' + assignment.detail.user.email : '' }}
                        </span>
                    </li>
                </ul>

                <button
                    v-if="emailSendingErr_showToggle && !emailSendingErr_isExpanded"
                    class="toggle-link"
                    type="button"
                    @click="emailSendingErr_toggleExpanded"
                >
                    show more...
                </button>
            </div>
        </div>
    </template>

    <!-- General request error template-->
    <template v-if="requestErrorData">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong> Failed to add user(s) with {{ reqErr_roleName }} role:
                </div>

                <template v-if="isAbstractRole">
                    <ul class="notification-list organization-list">
                        <li
                            v-for="client in reqErr_visibleClients"
                            :key="client.forest_client_number"
                            class="notification-list-item"
                        >
                            Organization -
                            {{
                                formatForestClientDisplayName(
                                    client.forest_client_number,
                                    client.client_name
                                )
                            }}
                        </li>

                        <li
                            v-if="reqErr_remainingClients > 0 && !reqErr_showAllClients"
                            class="notification-list-item see-more"
                        >
                            and {{ reqErr_remainingClients }} more...
                            <button
                                type="button"
                                class="btn-see-all"
                                @click="reqErr_showAllClients = true"
                            >
                                Show more...
                            </button>
                        </li>
                    </ul>
                </template>

                <ul class="notification-list user-list">
                    <li
                        v-for="user in reqErr_visibleUsers"
                        :key="user.userId"
                        class="notification-list-item"
                    >
                        <DotMarkIcon class="dot-mark-icon" />
                        <span>
                            {{
                                formatUserNameAndId(
                                    user.userId,
                                    user.firstName,
                                    user.lastName
                                )
                            }}
                        </span>
                    </li>

                    <li
                        v-if="reqErr_remainingUsers > 0 && !reqErr_showAllUsers"
                        class="notification-list-item see-more"
                    >
                        and {{ reqErr_remainingUsers }} more...
                        <button
                            type="button"
                            class="btn-see-all"
                            @click="reqErr_showAllUsers = true"
                        >
                            Show more...
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </template>
</template>

<style scoped lang="scss">
 .failed-permission-content {
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

            &.see-more {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
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

.btn-see-all {
    background-color: transparent;
    border: none;
    color: var(--link-primary);
    padding: 0;
    cursor: pointer;
}

.btn-see-all:hover {
    color: var(--link-primary-hover);
}
</style>
