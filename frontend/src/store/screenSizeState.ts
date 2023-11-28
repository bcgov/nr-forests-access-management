import {sideNavState } from "@/store/SideNavState";

export const screenSize = () => {
     return window.innerWidth
};


window.addEventListener("resize", (event) => {
    sideNavState.isVisible = isDesktop();
});


export const isDesktop = () => {
    return screenSize() >= 1024
};
