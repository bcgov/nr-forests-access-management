import { shallowReactive, ref } from 'vue';
import { profileSidebarState } from '@/store/ProfileSidebarState';

export const sideNavState = shallowReactive({
    isVisible: window.innerWidth >= 1024,
    toggleSideNavVisible() {
        this.isVisible = !this.isVisible
        profileSidebarState.isVisible = false
    }
})