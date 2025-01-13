<script setup lang="ts">
import { useRouter, type RouteRecordName } from "vue-router";
import { sideNavState } from "@/store/SideNavState";
import EmailIcon from "@carbon/icons-vue/es/email/16";
import Sidebar from "primevue/sidebar";
import { sideNavItems } from "@/constants/SideNavConfig";
import Label from "@/components/UI/Label.vue";

const router = useRouter();

const getRoutePathByName = (routeName: RouteRecordName): string | undefined => {
    const route = router.getRoutes().find((r) => r.name === routeName);
    return route ? route.path : undefined;
};

/**
 * Checks if a menu item should be highlighted based on the current route path.
 *
 * @param {RouteRecordName} itemRouteName - The route name for the primary menu item.
 * @param {RouteRecordName[]} [subRouteNames] - Optional. Array of sub-route names to check for highlighting.
 * @returns {boolean} True if the current route matches the side nav item path or any of the sub-route paths; otherwise, false.
 */
const isMenuItemHighlighted = (
    itemRouteName: RouteRecordName,
    subRouteNames?: RouteRecordName[]
): boolean => {
    const currentRoutePath = router.currentRoute.value.path;
    const sideNavPath = getRoutePathByName(itemRouteName as string);

    if (!sideNavPath) {
        return false;
    }

    // Resolve paths of subRouteNames and check if the current route matches any of them
    const subRoutePaths = subRouteNames
        ? subRouteNames.map((name) => getRoutePathByName(name))
        : [];

    // Check if the current route starts with the side nav item's route or matches any sub-route
    return (
        currentRoutePath.startsWith(sideNavPath) ||
        subRoutePaths.some((path) => path && currentRoutePath.startsWith(path))
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
                            v-for="subMenuItem in item.subMenuItems"
                            :class="[
                                'sub-menu-item',
                                {
                                    'sidenav-selected': isMenuItemHighlighted(
                                        subMenuItem.routeName
                                    ),
                                    'sidenav-disabled': subMenuItem.disabled,
                                },
                            ]"
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
                <ul>
                    <Label label-text="Support" />
                    <li class="sub-menu-item">
                        <EmailIcon />
                        <a href="mailto:heartwood@gov.bc.ca">Contact us</a>
                    </li>
                </ul>
            </div>
        </nav>
    </Sidebar>
</template>
<style lang="scss" scoped>
.fam-sidenav {
    .sidenav {
        position: fixed;
        padding: 1rem 0;
        width: 100%;
        height: calc(100vh - 3.125rem - env(safe-area-inset-bottom));
        padding-bottom: calc(1rem + env(safe-area-inset-bottom));
        left: 0;
        overflow: hidden auto;

        .content {
            position: relative;
            min-height: auto;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;

            .fam-label {
                // Should use padding here but primevue-components-overrides.scss
                // has !important for all <label>
                margin: 1rem;
            }

            .sub-menu-item {
                a {
                    @include type.type-style("heading-compact-01");
                    color: var(--text-secondary);
                    text-decoration: none;
                }
            }
        }

        ul {
            padding: 0;
            margin: 0;
            list-style: none;
        }

        li {
            @include type.type-style("heading-compact-01");
            color: var(--text-secondary);

            padding: 0.9375rem 1rem;
            display: flex;
            flex-direction: row;
            align-items: center;

            svg {
                margin-right: 1.5rem;
                fill: var(--link-primary);
            }

            p {
                margin: 0;
            }

            &.sub-menu-item > span {
                margin-left: 1.5rem;
            }

            &:hover {
                background: var(--layer-hover-01);
                color: var(--text-primary);
                cursor: pointer;
            }

            &.sidenav-selected {
                background: var(--layer-selected-01);
                box-shadow: inset 0.25rem 0rem 0rem var(--border-interactive);
                color: var(--text-primary);
                font-weight: 700;

                &:hover {
                    background: var(--layer-selected-hover-01);
                }
            }

            &.sidenav-disabled {
                color: var(--text-disabled);
                cursor: not-allowed;

                svg {
                    fill: var(--text-disabled);
                }

                &:hover {
                    background: none;

                    color: var(--text-disabled);
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

@media (max-width: 768px) and (hover: none) and (pointer: coarse) {
    @supports (-webkit-touch-callout: none) {
        .fam-sidenav .sidenav {
            height: calc(
                100vh - 3.125rem - (env(safe-area-inset-bottom, 0) + 4rem)
            );
        }
    }
}
</style>
