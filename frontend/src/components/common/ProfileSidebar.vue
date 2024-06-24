<script setup lang="ts">
import { computed, ref } from 'vue';
import Avatar from 'primevue/avatar';
import Button from '@/components/common/Button.vue';
import { IconPosition, IconSize } from '@/enum/IconEnum';
import authService from '@/services/AuthService';
import LoginUserState from '@/store/FamLoginUserState';
import { profileSidebarState } from '@/store/ProfileSidebarState';
import { toggleCloseble } from '@/store/TermsAndConditionsState';

const userName = LoginUserState.state.value.famLoginUser!.username;
const initials = userName ? userName.slice(0, 2) : '';
const displayName = LoginUserState.state.value.famLoginUser!.displayName;
const email = LoginUserState.state.value.famLoginUser!.email;
const organization = LoginUserState.state.value.famLoginUser!.organization;

// use local loading state, can't use LoadingState instance
// due to logout() is handled by library.
const loading = ref(false);

const logout = () => {
    authService.logout();
    loading.value = true;
};

const showTerms = () => {
    toggleCloseble();
    showTerms();
    profileSidebarState.toggleVisible();
};

const buttonLabel = computed(() => {
    return loading.value ? 'Signing out...' : 'Sign out';
});

const adminRoles = computed(() => {
    const userAdminRoles = LoginUserState.getUserAdminRoleGroups();
    if (userAdminRoles) {
        return userAdminRoles
            .map((adminRole) => {
                return adminRole.replace('_', ' ');
            })
            .join(', ');
    }
});
</script>

<template>
    <div
        :class="profileSidebarState.isVisible ? 'fade-in' : 'fade-out'"
        @click="profileSidebarState.toggleVisible()"
    ></div>
    <Transition name="slide">
        <div
            class="profile-container"
            v-if="profileSidebarState.isVisible"
        >
            <div class="profile-header">
                <h2>Profile</h2>
                <button
                    class="btn-icon"
                    @click="profileSidebarState.toggleVisible()"
                    aria-label="Close profile sidebar"
                >
                    <Icon
                        icon="close"
                        :size="IconSize.small"
                    ></Icon>
                </button>
            </div>
            <div class="sidebar-body">
                <Avatar
                    :label="initials"
                    class="mr-2 profile-avatar"
                    size="xlarge"
                    shape="circle"
                />
                <div class="profile-info">
                    <p class="profile-name">{{ displayName }}</p>
                    <p class="profile-userid">
                        {{ LoginUserState.getUserIdpProvider() }}:
                        {{ userName }}
                    </p>
                    <p
                        class="profile-organization"
                        v-if="organization"
                    >
                        Organization: {{ organization }}
                    </p>
                    <p class="profile-email">Email: {{ email }}</p>
                    <p class="profile-admin-level">
                        Granted: <strong>{{ adminRoles }}</strong>
                    </p>
                </div>
            </div>
            <Divider class="profile-divider" />
            <Button
                class="profile-sidebar-btn"
                title="Terms of use"
                aria-expanded="false"
                aria-label="show terms of use"
                :iconPosition="IconPosition.left"
                label="Terms of use"
                @click="showTerms()"
            >
                <Icon
                    title="terms of use"
                    icon="document"
                    :size="IconSize.small"
                    class="custom-carbon-icon-document"
                />
            </Button>
            <Button
                class="profile-sidebar-btn"
                title="Sign out"
                aria-expanded="false"
                aria-label="sign out"
                :iconPosition="IconPosition.left"
                :label="buttonLabel"
                @click="logout"
                :disabled="loading ? true : false"
            >
                <Icon
                    title="Sign out"
                    icon="user--follow"
                    :size="IconSize.small"
                    class="custom-carbon-icon-user--follow"
                />
            </Button>
        </div>
    </Transition>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
@import '@/assets/styles/base.scss';

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

.profile-sidebar-btn:hover,
.profile-sidebar-btn:active,
.profile-sidebar-btn:focus {
    background-color: $light-border-subtle-00 !important;
    box-shadow: none !important;
    outline: none !important;
}

.profile-userid,
.profile-organization,
.profile-email,
.profile-admin-level,
.options {
    font-size: 0.75rem;
    font-weight: 400;
}

.profile-divider {
    margin: 1rem 0 !important;
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
    background-color: #ffffff;
    color: $light-text-secondary !important;

    i {
        margin-right: 1.125rem;
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
