<script setup lang="ts">
import authService from '@/services/AuthService';
import { useProfileSidebarVisible } from '../../store/useProfileVisibleStore';

// svg icon
import CloseIcon from '../icons/CloseIcon.vue';
import LogoutIcon from '../icons/LogoutIcon.vue';
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
                    <CloseIcon />
                </button>
            </div>
            <!-- <div class="sidebar-body">
                <div class="img-wrapper">
                    <img
                        src="../../assets/images/tyrannosaurus-rex1.png"
                        alt="User avatar"
                    />
                </div>
                <div class="profile-info">
                    <p class="profile-name">
                        {{ authService.state.value.famLoginUser?.username }}
                    </p>
                    <p class="profile-idir">
                        IDIR:
                    </p>
                    <p class="profile-email">
                        email
                    </p>
                </div>
            </div> -->
            <hr class="profile-divider" />
            <p class="options">Options</p>
            <button
                class="sign-out"
                title="Sign out"
                aria-expanded="false"
                aria-label="sign out"
                @click="authService.methods.logout"
            >
                <i><LogoutIcon /></i>
                Sign out
            </button>
        </div>
    </Transition>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.profile-container {
    background-color: #fff;
    border-left: 1px solid #dfdfe1;
    color: #000;
    height: calc(100vh - 48px);
    inset: 0 0 0 70%;
    margin: 48px 0 0;
    padding: 0 16px 0;
    position: fixed;
    overflow: hidden;
    z-index: 9999;
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 16px 0;

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
    margin: 30px 0 0;

    .img-wrapper {
        margin-right: 32px;
    }

    .profile-info {
        margin: 6px 0 0;
        display: flex;
        flex-direction: column;
    }

    .profile-name,
    .profile-idir {
        margin-bottom: 6px;
    }
}

.profile-name,
.sign-out {
    font-size: 14px;
    font-weight: 700;
}

.sign-out:hover {
    background-color: transparent;
    background-color: #ffffff;
}

.profile-idir,
.profile-email,
.options {
    font-size: 12px;
    font-weight: 400;
}

.profile-divider {
    background: #ffffff;
    background-blend-mode: multiply;
    margin: 16px 0;
}

.sign-out {
    border: none;
    background-color: transparent;
    color: #000;
    cursor: pointer;

    i {
        margin-right: 18px;
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
    inset: 48px 0 0 0;
    z-index: 999;
}

.fade-out {
    visibility: hidden;
    background-color: rgba($color: #131315, $alpha: 0);
}
</style>
