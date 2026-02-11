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

const assignments = props.assignments ?? [];

//--- 409 conflict case setup (user already has the role assignment)
const conflictErr_assignmentsMap = mapAppUserGrantResponseByUserId(
    (assignments ?? []).filter((a) => a.status_code === 409)
);
const conflictErr_userIds = Array.from(conflictErr_assignmentsMap.keys());
const conflictErr_headerText = `${assignments[0]?.detail?.role?.display_name} role already exists for the following users`
const conflictErr_isExpanded = ref(false);
const conflictErr_showToggle = conflictErr_userIds.length > PREVIEW_LIMIT;
const conflictErr_visibleUserIds = computed(() => {
    if (!conflictErr_showToggle || conflictErr_isExpanded.value) {
        return conflictErr_userIds;
    }
    return conflictErr_userIds.slice(0, PREVIEW_LIMIT);
});
const conflictErr_toggleExpanded = () => {
    conflictErr_isExpanded.value = !conflictErr_isExpanded.value;
};

//--- Email seinding failure case setup
const emailSendingErr_headerText = `Email notifications could not be sent to some users`;

// grouped by user ID and use first result per user for notification
const emailSendingErr_assignments = Array.from(
    mapAppUserGrantResponseByUserId(
        (assignments ?? []).filter(
            (a) => a.email_sending_status === EmailSendingStatus.SentToEmailServiceFailure
        )
    ).values()
).map((items) => items[0]);

const emailSendingErr_isExpanded = ref(false);
const emailSendingErr_showToggle = emailSendingErr_assignments.length > PREVIEW_LIMIT;
const emailSendingErr_visibleAssignments = computed(() => {
    if (!emailSendingErr_showToggle || emailSendingErr_isExpanded.value) {
        return emailSendingErr_assignments;
    }
    return emailSendingErr_assignments.slice(0, PREVIEW_LIMIT);
});
const emailSendingErr_toggleExpanded = () => {
    emailSendingErr_isExpanded.value = !emailSendingErr_isExpanded.value;
};

//--- 500 internal error during granting assignment for individual user.

// Backend will have no 'detail' field but error_message is available.
const internalErr_assignments = (assignments ?? []).filter(
    (a) => a.status_code >= 500
)

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
    <!-- 409 user role exists error template -->
    <template v-if="conflictErr_userIds && conflictErr_userIds.length > 0">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong> {{ conflictErr_headerText }}:
                </div>

                <button
                    v-if="conflictErr_showToggle && conflictErr_isExpanded"
                    class="toggle-link"
                    type="button"
                    @click="conflictErr_toggleExpanded"
                >
                    show less...
                </button>

                <ul class="notification-list user-list">
                    <li
                        v-for="userId in conflictErr_visibleUserIds"
                        :key="userId"
                        class="notification-list-item"
                    >
                        <DotMarkIcon class="dot-mark-icon" />
                        <span>
                            {{
                                formatUserNameAndId(
                                    conflictErr_assignmentsMap.get(userId)![0].detail!.user.user_name,
                                    conflictErr_assignmentsMap.get(userId)![0].detail!.user.first_name,
                                    conflictErr_assignmentsMap.get(userId)![0].detail!.user.last_name
                                )
                            }}
                        </span>
                        <div
                            v-if="conflictErr_assignmentsMap.get(userId)!.some(a => a.detail!.role?.forest_client)"
                            class="orgination-list"
                        >
                            with organizations:
                            <span class="org-names">
                                <template v-for="(assignment, idx) in conflictErr_assignmentsMap.get(userId)" :key="assignment.detail!.role?.forest_client?.forest_client_number">
                                    <template v-if="assignment.detail!.role?.forest_client">
                                        {{ assignment.detail!.role.forest_client.client_name +'(' + assignment.detail!.role.forest_client.forest_client_number + ')'}}
                                        <span v-if="idx < conflictErr_assignmentsMap.get(userId)!.length - 1">, </span>
                                    </template>
                                </template>
                            </span>
                        </div>
                    </li>
                </ul>

                <button
                    v-if="conflictErr_showToggle && !conflictErr_isExpanded"
                    class="toggle-link"
                    type="button"
                    @click="conflictErr_toggleExpanded"
                >
                    show more...
                </button>
            </div>
        </div>
    </template>

    <!-- Email sending error template -->
    <template v-if="emailSendingErr_assignments && emailSendingErr_assignments.length > 0">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong>: {{ emailSendingErr_headerText }}:
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
                            }} {{ assignment.detail!.user.email ? ' - ' + assignment.detail!.user.email : '' }}
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

    <!-- Internal error template -->
    <template v-if="internalErr_assignments && internalErr_assignments.length > 0">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong>: An unexpected error occurred:
                </div>

                <ul class="notification-list user-list">
                    <li
                        v-for="assignment in internalErr_assignments"
                        class="notification-list-item"
                    >
                        <DotMarkIcon class="dot-mark-icon" />
                        <span>
                            {{ assignment.error_message!.length > 125 ? assignment.error_message!.slice(0, 125) + '...' : assignment.error_message }}
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </template>

    <!-- General request error template -->
    <template v-if="requestErrorData">
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong>: Failed to add user(s) with {{ reqErr_roleName }} role:
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
    margin-bottom: 0.5rem;

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

.orgination-list {
    margin-left: 1rem;
    font-size: 0.97em;
    color: #333;
    word-break: break-word;
    white-space: normal;
    line-height: 1.5;
    max-width: 100%;
}
.org-names {
    display: inline;
    word-break: break-word;
    white-space: normal;
    margin-bottom: 0.7rem;
}
</style>
