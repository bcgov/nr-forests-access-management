import { sideNavState } from "@/store/SideNavState";

export let screenSize = window.innerWidth

window.addEventListener("resize", (event) => {
    screenSize = window.innerWidth
    sideNavState.isVisible = isDesktop()
});


export const isDesktop = () => {
    return screenSize >= 1024
}
