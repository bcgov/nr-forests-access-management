import { shallowReactive } from "vue";
import { sideNavState } from "@/store/SideNavState";
import { isDesktop } from "@/store/screenSizeState";

export const profileSidebarState = shallowReactive({
    isVisible: false,
    toggleVisible() {
        this.isVisible = !this.isVisible;
        sideNavState.isVisible = isDesktop();
    },
});
