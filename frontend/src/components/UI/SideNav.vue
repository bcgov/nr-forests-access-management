<script setup lang="ts">
import { useRouter, type RouteRecordName } from "vue-router";
import { sideNavState } from "@/store/SideNavState";
import Sidebar from "primevue/sidebar";
import { sideNavItems } from "@/constants/SideNavConfig";

const router = useRouter();

/**
 * Determines if a menu item is highlighted based on the current route.
 *
 * @param {RouteRecordName} itemRouteName - The route name associated with the menu item.
 * @param {RouteRecordName[]} [subRouteNames] - Optional. An array of sub-route names that should be considered for highlighting.
 * @returns {boolean} True if the menu item or any of its sub-route names match the current route; otherwise, false.
 */
const isMenuItemHighlighted = (
    itemRouteName: RouteRecordName,
    subRouteNames?: RouteRecordName[]
): boolean => {
    const currentRouteName = router.currentRoute.value.name;

    // Check if the current route matches the item route or any sub-routes
    return (
        currentRouteName === itemRouteName ||
        (subRouteNames
            ? subRouteNames.includes(currentRouteName as RouteRecordName)
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
                                    item.routeName,
                                    item.subRoutes
                                ),
                                'sidenav-disabled': item.disabled,
                            }"
                            @click="
                                item.disabled
                                    ? () => {}
                                    : router.push({ name: item.routeName })
                            "
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
                                    subMenuItem.routeName
                                ),
                                'sidenav-disabled': subMenuItem.disabled,
                            }"
                            @click="
                                subMenuItem.disabled
                                    ? () => {}
                                    : router.push({
                                          name: subMenuItem.routeName,
                                      })
                            "
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

            &.sidenav-disabled {
                color: colors.$gray-30;
                cursor: not-allowed;

                svg {
                    fill: colors.$gray-30;
                }

                &:hover {
                    background: none;

                    color: colors.$gray-30;
                    cursor: not-allowed;
                }
            }
        }
    }

    @media (min-width: 768px) {
        .sidenav {
            width: 100%;
        }
    }
}
</style>
