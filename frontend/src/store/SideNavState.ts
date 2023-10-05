import { reactive } from 'vue'

export const useSideNavVisible = reactive({
    isSideNavVisible: window.innerWidth >= 1024 ? true : false,
    toggleSideNavVisible() {
        this.isSideNavVisible = !this.isSideNavVisible
    }
})