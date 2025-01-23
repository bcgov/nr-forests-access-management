import { profileSidebarState } from "@/store/ProfileSidebarState";
import { isDesktop, isSmallScreen } from "@/store/screenSizeState";
import { shallowReactive } from "vue";

export const sideNavState = shallowReactive({
    isVisible: isDesktop(),
    toggleVisible() {
        // Only toggle the side nav if the screen is small
        if (isSmallScreen()) {
            this.isVisible = !this.isVisible;
            profileSidebarState.isVisible = false;
        }
    },
});
