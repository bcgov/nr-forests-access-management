<script setup lang="ts">
import { useRouter } from "vue-router";
import { sideNavState } from "@/store/SideNavState";
import Sidebar from "primevue/sidebar";
import { sideNavItems } from "@/constants/SideNavConfig";

const router = useRouter();

/**
 * Determines if a menu item is highlighted based on the current route.
 *
 * @param {string} itemLink - The link associated with the menu item.
 * @param {string[]} [childLinks] - Optional. An array of child links that should be considered for highlighting.
 * @returns {boolean} True if the menu item or any of its child links match the current route; otherwise, false.
 */
const isMenuItemHighlighted = (
    itemLink: string,
    childLinks?: string[]
): boolean => {
    const currentPath = router.currentRoute.value.path;

    // Check if the current path matches the item link or if any child links are matched
    return (
        currentPath === itemLink ||
        (childLinks
            ? childLinks.some((child) => currentPath.includes(child))
            : false)
    );
};
</script>
<template>
    <Sidebar class="fam-sidenav" v-model:visible="sideNavState.isVisible">
        <nav class="sidenav">
            <div class="content">
                <ul>
                    <template v-for="item in sideNavItems">
                        <li
                            :class="{
                                'sidenav-selected': isMenuItemHighlighted(
                                    item.link,
                                    item.childLinks
                                ),
                                'sidenav-disabled': item.disabled,
                            }"
                            @click="router.push(item.link)"
                        >
                            <component v-if="item.icon" :is="item.icon" />
                            <p>
                                {{ item.name }}
                            </p>
                        </li>
                        <li
                            class="sub-menu-item"
                            v-for="subMenuItem in item.subMenuItems"
                            :class="{
                                'sidenav-selected': isMenuItemHighlighted(
                                    subMenuItem.link
                                ),
                                'sidenav-disabled': subMenuItem.disabled,
                            }"
                            @click="router.push(subMenuItem.link)"
                        >
                            <span>{{ subMenuItem.name }}</span>
                        </li>
                    </template>
                </ul>
            </div>
        </nav>
    </Sidebar>
</template>
<style lang="scss" scoped>
@import "@/assets/styles/styles.scss";

.fam-sidenav {
    .sidenav {
        position: fixed;
        padding: 1rem 0;
        width: 100%;
        height: calc(100vh - 3.125rem);
        left: 0;
        overflow: hidden auto;

        .content {
            position: relative;
            min-height: auto;
        }

        ul {
            padding: 0;
            margin: 0;
            list-style: none;
        }

        li {
            @extend %helper-text-01;
            color: $light-text-secondary;
            font-size: 1rem;
            font-weight: 400;
            padding: 0.9375rem 1rem;
            display: flex;
            flex-direction: row;
            align-items: center;

            svg {
                margin-right: 1.5rem;
                fill: colors.$blue-70;
            }

            a {
                text-decoration: none;
            }

            p {
                margin: 0;
            }

            &.sub-menu-item > span {
                margin-left: 1.5rem;
            }

            &:hover {
                background: $light-layer-hover-01;
                color: $light-text-primary;
                cursor: pointer;
            }

            &.sidenav-selected {
                background: $light-layer-selected-01;
                box-shadow: inset 0.25rem 0rem 0rem $light-border-interactive;
                color: $light-text-primary;
                font-weight: 700;

                &:hover {
                    background: $light-layer-selected-hover-01;
                }
            }
        }

        &-disabled {
            display: none;
        }
    }

    @media (min-width: 768px) {
        .sidenav {
            width: 100%;
        }
    }
}
</style>
