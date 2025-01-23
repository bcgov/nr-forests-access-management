import { sideNavState } from "@/store/SideNavState";

export const screenSize = () => {
    return window.innerWidth;
};

window.addEventListener("resize", (event) => {
    sideNavState.isVisible = isDesktop();
});

const isDesktop = () => {
    return screenSize() >= 1024;
};

const isSmallScreen = () => {
    return !isDesktop();
};

export { isDesktop, isSmallScreen };
