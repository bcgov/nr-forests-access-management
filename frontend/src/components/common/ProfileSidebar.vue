<script setup lang="ts">
import { ref, computed } from 'vue';
import Button from './Button.vue';

import authService from '@/services/AuthService';
import { useProfileSidebarVisible } from '@/store/ProfileVisibleState';
import { IconPosition, IconSize } from '@/enum/IconEnum';

const userName = authService.state.value.famLoginUser!.username;
const loading = ref(false);
const logout = () => {
    authService.methods.logout();
    loading.value = true;
};

const buttonLabel = computed(() => {
    return loading.value ? 'Signing out...' : 'Sign out';
});
</script>

<template>
    <div
        :class="
            useProfileSidebarVisible.isProfileVisible ? 'fade-in' : 'fade-out'
        "
        @click="useProfileSidebarVisible.toggleVisible()"
    ></div>
    <Transition name="slide">
        <div
            class="profile-container"
            v-if="useProfileSidebarVisible.isProfileVisible"
        >
            <div class="profile-header">
                <h2>Profile</h2>
                <button
                    class="btn-icon"
                    @click="useProfileSidebarVisible.toggleVisible()"
                    aria-label="Close"
                >
                    <Icon icon="close" :size="IconSize.small"></Icon>
                </button>
            </div>
            <div class="sidebar-body">
                <!-- TODO - This code below is for displaying user information when it is available -->
                <!-- <div class="img-wrapper">
                    <img
                        src="../../assets/images/tyrannosaurus-rex1.png"
                        alt="User avatar"
                    />
                </div> -->
                <div class="profile-info">
                    <p class="profile-name">
                        {{ userName }}
                    </p>
                    <!-- TODO - This code below is for displaying user information when it is available -->
                    <!-- <p class="profile-idir">IDIR:</p>
                    <p class="profile-email">email</p> -->
                </div>
            </div>
            <hr class="profile-divider" />
            <p class="options">Options</p>
            <Button
                class="sign-out"
                title="Sign out"
                aria-expanded="false"
                aria-label="sign out"
                :label="buttonLabel"
                :iconpos="IconPosition.left"
                @click="logout"
                :disabled="loading ? true : false"
            >
                <Icon
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
.profile-container {
    background-color: #fff;
    border-left: 0.0625rem solid #dfdfe1;
    color: #000;
    height: calc(100vh - 3rem);
    inset: 0 0 0 70%;
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

    .img-wrapper {
        margin-right: 2rem;
    }

    .profile-info {
        margin: 0.375rem 0 0;
        display: flex;
        flex-direction: column;
    }

    .profile-name,
    .profile-idir {
        margin-bottom: 0.375rem;
    }
}

.profile-name,
.sign-out {
    font-size: 0.875rem;
    font-weight: 700;
    display: flex;
    border: none;
    cursor: pointer;
}

.sign-out,
.sign-out:hover:focus {
    background-color: transparent;
    background-color: #ffffff !important;
    color: $light-text-secondary !important;
    box-shadow: none !important;
}

.profile-idir,
.profile-email,
.options {
    font-size: 0.75rem;
    font-weight: 400;
}

.profile-divider {
    background: #ffffff;
    background-blend-mode: multiply;
    margin: 1rem 0;
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
    z-index: 999;
}

.fade-out {
    visibility: hidden;
    background-color: rgba($color: #131315, $alpha: 0);
}
</style>
