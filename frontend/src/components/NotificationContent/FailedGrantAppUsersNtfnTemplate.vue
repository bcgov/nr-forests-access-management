<script setup lang="ts">
import { formatForestClientDisplayName } from "@/utils/ForestClientUtils";
import { formatUserNameAndId } from "@/utils/UserUtils";
import type { AppPermissionQueryErrorType } from "@/views/AddAppPermission/utils";
import DotMarkIcon from "@carbon/icons-vue/es/dot-mark/16";
import MisuseIcon from "@carbon/icons-vue/es/misuse/20";
import { RoleType } from "fam-admin-mgmt-api/model";
import { type FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api/model";
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

const headerText_failedEmailSending = `Failed to send email for permissions granted in ${props.applicationName ?? "this application"}. Please contact users:`;

const PREVIEW_LIMIT = 2;

//--- properties for requestErrorData (general error case)
const showAllUsers = ref(false);
const showAllClients = ref(false);

const roleName = props.requestErrorData?.formData.role?.display_name;
const isAbstractRole = props.requestErrorData?.formData.role?.type_code === RoleType.A;
const users = props.requestErrorData?.formData.users ?? [];
const forestClients = props.requestErrorData?.formData.forestClients ?? [];
const visibleUsers = computed(() => showAllUsers.value ? users : users.slice(0, PREVIEW_LIMIT));
const remainingUsers = Math.max(users.length - PREVIEW_LIMIT, 0);
const visibleClients = computed(() => showAllClients.value ? forestClients : forestClients.slice(0, PREVIEW_LIMIT));
const remainingClients = Math.max(forestClients.length - PREVIEW_LIMIT, 0);
</script>

<template>
    <template v-if="assignments">
        <div class="failed-permission-content">
            <div class="notification-header">
                {{ headerText_failedEmailSending }}
            </div>
        </div>
    </template>

    <template v-else>
        <div class="failed-permission-content">
            <MisuseIcon />
            <div class="notification-body">
                <div class="notification-header">
                    <strong>Error</strong> Failed to add user(s) with {{ roleName }} role:
                </div>

                <template v-if="isAbstractRole">
                    <ul class="notification-list organization-list">
                        <li
                            v-for="client in visibleClients"
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
                            v-if="remainingClients > 0 && !showAllClients"
                            class="notification-list-item see-more"
                        >
                            and {{ remainingClients }} more...
                            <button
                                type="button"
                                class="btn-see-all"
                                @click="showAllClients = true"
                            >
                                Show more...
                            </button>
                        </li>
                    </ul>
                </template>

                <ul class="notification-list user-list">
                    <li
                        v-for="user in visibleUsers"
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
                        v-if="remainingUsers > 0 && !showAllUsers"
                        class="notification-list-item see-more"
                    >
                        and {{ remainingUsers }} more...
                        <button
                            type="button"
                            class="btn-see-all"
                            @click="showAllUsers = true"
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
