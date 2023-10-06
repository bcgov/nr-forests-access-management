import { shallowReactive } from 'vue'

let screenSize = window.innerWidth

window.addEventListener("resize", (event) => {
    screenSize = window.innerWidth
    sideNavState.isVisible = sideNavState.isDesktop()
    sideNavState.isDesktopSize = sideNavState.isDesktop()
});

export const sideNavState = shallowReactive({
    isVisible: screenSize >= 1024 ? true : false,
    isDesktopSize: screenSize >= 1024,
    toggleSideNavVisible() {
        this.isVisible = !this.isVisible
    },
    isDesktop() {
        return screenSize >= 1024
    }
})