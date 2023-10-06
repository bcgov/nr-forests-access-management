import { reactive } from 'vue'


export const useSideNavVisible = reactive({
    isSideNavVisible: window.innerWidth >= 1024 ? true : false,
    isDesktopSize: false,
    toggleSideNavVisible() {
        this.isSideNavVisible = !this.isSideNavVisible
    },
    isDesktop() {
        return window.innerWidth >= 1024
    }
})

window.addEventListener("resize", (event) => {
    useSideNavVisible.isSideNavVisible = useSideNavVisible.isDesktop()
    useSideNavVisible.isDesktopSize = useSideNavVisible.isDesktop()
});