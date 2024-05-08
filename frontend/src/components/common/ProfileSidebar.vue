<script setup lang="ts">
import { computed, ref } from 'vue';
import Avatar from 'primevue/avatar';
import Button from '@/components/common/Button.vue';
import { IconSize } from '@/enum/IconEnum';
import { IdpProvider } from '@/enum/IdpEnum';
import authService from '@/services/AuthService';
import LoginUserState from '@/store/FamLoginUserState';
import { profileSidebarState } from '@/store/ProfileSidebarState';
import FamLoginUserState from '@/store/FamLoginUserState';

const userName = LoginUserState.state.value.famLoginUser!.username;
const initials = userName ? userName.slice(0, 2) : '';
const displayName = LoginUserState.state.value.famLoginUser!.displayName;
const email = LoginUserState.state.value.famLoginUser!.email;
const organization = LoginUserState.state.value.famLoginUser!.organization;
const userType =
    FamLoginUserState.getUserType() === IdpProvider.IDIR
        ? IdpProvider.IDIR
        : IdpProvider.BCEIDBUSINESS;

// use local loading state, can't use LoadingState instance
// due to logout() is handled by library.
const loading = ref(false);

const logout = () => {
    authService.logout();
    loading.value = true;
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
        <div class="profile-container" v-if="profileSidebarState.isVisible">
            <div class="profile-header">
                <h2>Profile</h2>
                <button
                    class="btn-icon"
                    @click="profileSidebarState.toggleVisible()"
                    aria-label="Close"
                >
                    <Icon icon="close" :size="IconSize.small"></Icon>
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
                    <p class="profile-userid">{{ userType }}: {{ userName }}</p>
                    <p class="profile-organization" v-if="organization">
                        Organization: {{ organization }}
                    </p>
                    <p class="profile-email">Email: {{ email }}</p>
                    <p class="profile-admin-level">
                        Granted: <strong>{{ adminRoles }}</strong>
                    </p>
                </div>
            </div>
            <Divider class="profile-divider" />
            <p class="options">Options</p>
            <div class="sign-out-wrapper">
                <Icon
                    title="Sign out"
                    icon="user--follow"
                    :size="IconSize.small"
                    class="custom-carbon-icon-user--follow"
                    @click="logout"
                    :disabled="loading ? true : false"
                />
                <Button
                    class="sign-out"
                    title="Sign out"
                    aria-expanded="false"
                    aria-label="sign out"
                    :label="buttonLabel"
                    @click="logout"
                    :disabled="loading ? true : false"
                >
                </Button>
            </div>
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
    inset: 0 0 0 0;
    margin: 3rem 0 0;
    padding: 0 1rem 0;
    position: fixed;
    overflow: hidden;
    z-index: 9999;
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

.sign-out-wrapper {
    display: flex;
}

.custom-carbon-icon-user--follow {
    margin: 0 1.2rem 0 0;
    cursor: pointer;
}

.profile-name,
.sign-out {
    font-size: 0.875rem;
    font-weight: 700;
    display: flex;
    border: none;
    cursor: pointer;
    padding: 0;
}

.sign-out,
.sign-out:hover:focus {
    background-color: transparent;
    background-color: #ffffff !important;
    color: $light-text-secondary !important;
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

.sign-out {
    border: none;
    background-color: transparent;
    color: #000;
    cursor: pointer;

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
    z-index: 1110;
}

.fade-out {
    visibility: hidden;
    background-color: rgba($color: #131315, $alpha: 0);
}

@media (min-width: 425px) {
    .profile-container {
        inset: 0 0 0 30%;
    }
}

@media (min-width: 600px) {
    .profile-container {
        inset: 0 0 0 50%;
    }
}

@media (min-width: 790px) {
    .profile-container {
        inset: 0 0 0 60%;
    }
}

@media (min-width: 900px) {
    .profile-container {
        inset: 0 0 0 60%;
    }
}

@media (min-width: 1366px) {
    .profile-container {
        inset: 0 0 0 70%;
    }
}
</style>
