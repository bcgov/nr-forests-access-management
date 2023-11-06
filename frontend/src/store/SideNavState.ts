import { shallowReactive } from 'vue'
import { profileSidebarState } from '@/store/ProfileSidebarState';

let initialScreen = window.innerWidth

export const sideNavState = shallowReactive({
    isVisible: initialScreen >= 1024,
    toggleSideNavVisible() {
        this.isVisible = !this.isVisible
        profileSidebarState.isVisible = false
    }
})