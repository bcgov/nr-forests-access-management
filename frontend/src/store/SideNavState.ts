import { shallowReactive } from "vue";
import { profileSidebarState } from "@/store/ProfileSidebarState";

export const sideNavState = shallowReactive({
    isVisible: window.innerWidth >= 1024,
    toggleVisible() {
        this.isVisible = !this.isVisible;
        profileSidebarState.isVisible = false;
    },
});
