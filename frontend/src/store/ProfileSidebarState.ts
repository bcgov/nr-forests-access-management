import { reactive } from 'vue'
import { sideNavState } from '@/store/SideNavState'

export const profileSidebarState = reactive({
    isVisible: false,
    toggleVisible() {
        this.isVisible = !this.isVisible
        sideNavState.isVisible = sideNavState.isDesktop()
    }
})