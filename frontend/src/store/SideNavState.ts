import { reactive } from 'vue'

export const useSideNavVisible = reactive({
    isSideNavVisible: false,
    toggleSideNavVisible() {
        this.isSideNavVisible = !this.isSideNavVisible
    }
})