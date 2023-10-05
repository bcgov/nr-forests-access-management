import { reactive } from 'vue'

export const useSideNavVisible = reactive({
    isSideNavVisible: false,
    isDesktopSize: false,
    toggleSideNavVisible() {
        this.isSideNavVisible = !this.isSideNavVisible
    },
    isDesktop() {
        return window.innerWidth >= 1024 && true
    }
})

window.addEventListener("resize", (event) => {
    useSideNavVisible.isSideNavVisible = useSideNavVisible.isDesktop()
    useSideNavVisible.isDesktopSize = useSideNavVisible.isDesktop()
});