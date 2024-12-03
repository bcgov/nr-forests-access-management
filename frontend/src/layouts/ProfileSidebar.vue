<script setup lang="ts">
import Button from "primevue/button";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import { default as FamButton } from "@/components/UI/Button.vue";
import LogoutIcon from "@carbon/icons-vue/es/logout/16";
import CloseIcon from "@carbon/icons-vue/es/close/16";
import DocumentIcon from "@carbon/icons-vue/es/document/16";
import { profileSidebarState } from "@/store/ProfileSidebarState";
import { showTermsForRead } from "@/store/TermsAndConditionsState";
import Avatar from "primevue/avatar";
import { computed, ref } from "vue";
import useAuth from "@/composables/useAuth";
import { useQuery } from "@tanstack/vue-query";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import PSkeleton from "@/components/Skeletons/PSkeleton.vue";

const auth = useAuth();
const famLoginUser = auth.authState.famLoginUser;

// use local loading state, can't use LoadingState instance
// due to logout() is handled by library.
const loading = ref(false);

const logout = () => {
    if (!loading.value) {
        auth.logout();
        loading.value = true;
    }
};

const showTermsAndConditions = () => {
    showTermsForRead();
    profileSidebarState.toggleVisible();
};

const buttonLabel = computed(() => {
    return loading.value ? "Signing out..." : "Sign out";
});

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
    select: (data) => {
        const accessList = data.access.map((grantDto) => grantDto.auth_key);

        const famAdminIndex = accessList.indexOf(AdminRoleAuthGroup.FamAdmin);
        if (famAdminIndex !== -1) {
            const famAdmin = accessList.splice(famAdminIndex, 1)[0];
            accessList.unshift(famAdmin);
        }

        return accessList.map((key) => key.replace("_", " ")).join(", ");
    },
});
</script>

<template>
    <div
        :class="profileSidebarState.isVisible ? 'fade-in' : 'fade-out'"
        @click="profileSidebarState.toggleVisible()"
    ></div>
    <Transition name="slide">
        <div class="profile-container" v-if="profileSidebarState.isVisible">
            <div class="profile-header">
                <h2>Profile</h2>
                <FamButton
                    class="btn-icon"
                    @click="profileSidebarState.toggleVisible()"
                    aria-label="Close profile sidebar"
                    :icon="CloseIcon"
                    text
                    icon-only
                >
                </FamButton>
            </div>
            <div class="sidebar-body">
                <Avatar
                    :label="
                        famLoginUser?.username
                            ? famLoginUser.username.slice(0, 2)
                            : ''
                    "
                    class="mr-2 profile-avatar"
                    size="xlarge"
                    shape="circle"
                />
                <div class="profile-info">
                    <p class="profile-name">{{ famLoginUser?.displayName }}</p>
                    <p class="profile-userid">
                        {{
                            `${
                                famLoginUser?.idpProvider === "idir"
                                    ? "IDIR: "
                                    : famLoginUser?.idpProvider ===
                                      "bceidbusiness"
                                    ? "BCeID: "
                                    : null
                            }`
                        }}
                        {{ famLoginUser?.username }}
                    </p>
                    <p
                        class="profile-organization"
                        v-if="famLoginUser?.organization"
                    >
                        Organization: {{ famLoginUser.organization }}
                    </p>
                    <p class="profile-email">
                        Email: {{ famLoginUser?.email }}
                    </p>
                    <p class="profile-admin-level">
                        Granted:&nbsp;
                        <PSkeleton
                            v-if="adminUserAccessQuery.isLoading.value"
                        />
                        <strong v-else>
                            {{ adminUserAccessQuery.data.value }}
                        </strong>
                    </p>
                </div>
            </div>
            <Divider class="profile-divider" />
            <Button
                v-if="
                    famLoginUser?.idpProvider === 'bceidbusiness' &&
                    adminUserAccessQuery.data.value
                        ?.toLowerCase()
                        .includes('delegated admin')
                "
                class="profile-sidebar-btn"
                title="Terms of use"
                aria-expanded="false"
                aria-label="show terms of use"
                label="Terms of use"
                @click="showTermsAndConditions()"
            >
                <template #default>
                    <DocumentIcon />
                    <span>Terms of use</span>
                </template>
            </Button>
            <Button
                class="profile-sidebar-btn"
                aria-expanded="false"
                aria-label="sign out"
                :label="buttonLabel"
                @click="logout"
            >
                <template #default>
                    <LogoutIcon />
                    <span>{{ buttonLabel }}</span>
                </template>
            </Button>
        </div>
    </Transition>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/base.scss";

.profile-container {
    background-color: #fff;
    border-left: 0.0625rem solid #dfdfe1;
    color: #000;
    height: calc(100vh - 3rem);
    width: 25rem;
    margin: 3rem 0 0 0;
    padding: 0 1rem;
    position: fixed;
    overflow: hidden;
    z-index: 1103;
    right: 0;
    left: auto;
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1rem 0;

    h2 {
        margin: 0;
        font-weight: 400;
    }

    .btn-icon {
        border: none;
        background-color: transparent;

        &:enabled:hover {
            background-color: transparent;
        }
    }
}

.sidebar-body {
    display: flex;
    margin: 1.875rem 0 0;

    .profile-avatar {
        margin-right: 2rem;
        margin-top: 0.5rem;
        flex-shrink: 0;
        background: $light-background-brand;
        color: $dark-text-primary;
    }

    .profile-info {
        margin: 0.375rem 0 0;
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    .profile-name,
    .profile-userid,
    .profile-organization,
    .profile-email {
        margin-bottom: 0.375rem;
    }
}

.custom-carbon-icon-user--follow,
.custom-carbon-icon-document {
    margin: 0;
    cursor: pointer;
}

.profile-name,
.profile-sidebar-btn {
    font-size: 0.875rem;
    font-weight: 700;
    display: flex;
    border: none;
    padding: 0;
}

.profile-sidebar-btn:enabled:hover,
.profile-sidebar-btn:enabled:active,
.profile-sidebar-btn:enabled:focus {
    background-color: $light-border-subtle-00;
    box-shadow: none;
    outline: none;
}

.profile-userid,
.profile-organization,
.profile-email,
.profile-admin-level,
.options {
    font-size: 0.75rem;
    font-weight: 400;
}

.profile-admin-level {
    display: flex;
    flex-direction: row;
}

.profile-divider {
    margin: 1rem 0;
}

.profile-sidebar-btn {
    cursor: pointer;
    border: none;
    background-color: transparent;
    color: #000;
    width: calc(100% + 2rem);
    height: 3rem;
    border-radius: 0;
    padding-left: 1rem;
    margin-left: -1rem;

    svg {
        margin-right: 1.125rem;
        fill: colors.$blue-60;
    }
}

/// profile sidebar slide animation
.slide-enter-active,
.slide-leave-active {
    transform: translateX(0%);
    transition: ease-out 350ms;
}

.slide-enter-from,
.slide-leave-to {
    transform: translateX(100%);
    transition: ease-out 350ms;
}

/// background fade transition
.fade-in,
.fade-out {
    background-color: rgba($color: #131315, $alpha: 0.5);
    transition: ease-in 350ms;
    position: fixed;
    width: 100%;
    inset: 3rem 0 0 0;
    z-index: 1102;
}

.fade-out {
    visibility: hidden;
    background-color: rgba($color: #131315, $alpha: 0);
}

@media (max-width: 400px) {
    .profile-container {
        width: 100vw;
    }
}
</style>
