import { shallowReactive } from 'vue'
import { profileSidebarState } from '@/store/ProfileSidebarState';

let screenSize = window.innerWidth

window.addEventListener("resize", (event) => {
    screenSize = window.innerWidth
    sideNavState.isVisible = sideNavState.isDesktop()
});

export const sideNavState = shallowReactive({
    isVisible: screenSize >= 1024,
    toggleSideNavVisible() {
        this.isVisible = !this.isVisible
        profileSidebarState.isVisible = false
    },
    isDesktop() {
        return screenSize >= 1024
    }
})