<script setup lang="ts">
import Label from "@/components/UI/Label.vue";
import { sideNavItems } from "@/constants/SideNavConfig";
import { AdminMgmtApiService } from "@/services/ApiServiceFactory";
import { sideNavState } from "@/store/SideNavState";
import AlignBoxIcon from "@carbon/icons-vue/es/align-box--top-center/16";
import EmailIcon from "@carbon/icons-vue/es/email/16";
import { useQuery } from "@tanstack/vue-query";
import { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import { computed } from "vue";
import { useRouter, type RouteRecordName } from "vue-router";

const router = useRouter();

const adminUserAccessQuery = useQuery({
    queryKey: ["admin-user-access"],
    queryFn: () =>
        AdminMgmtApiService.adminUserAccessesApi
            .adminUserAccessPrivilege()
            .then((res) => res.data),
});

/**
 * Determines if a user is an app admin for at least one application,
 * @returns {string} a path to the relevant pdf file.
 */
const pathToPdfGuide = computed(() => {
    if (!adminUserAccessQuery.data.value) {
        return "";
    }

    const accessList = adminUserAccessQuery.data.value.access.map(
        (grantDto) => grantDto.auth_key
    );

    if (accessList.indexOf(AdminRoleAuthGroup.AppAdmin) > -1)
        return "/files/FAM_app-admin-instructions.pdf";

    if (accessList.indexOf(AdminRoleAuthGroup.DelegatedAdmin) > -1)
        return "/files/FAM_delegated-admin-instructions.pdf";
});

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

const navigateOnClick = (routeName: RouteRecordName) => {
    router.push({ name: routeName });
    sideNavState.toggleVisible();
};
</script>
<template>
    <div
        class="fam-sidenav"
        :class="{ 'is-visible': sideNavState.isVisible }"
        @click.self="sideNavState.toggleVisible()"
    >
        <nav class="sidenav">
            <div class="content">
                <ul>
                    <template v-for="item in sideNavItems" :key="item.routeName">
                        <li
                            :class="{
                                'sidenav-selected': isMenuItemHighlighted(
                                    item.routeName,
                                    item.subRoutes
                                ),
                                'sidenav-disabled': item.disabled,
                            }"
                            @click="navigateOnClick(item.routeName)"
                        >
                            <component v-if="item.icon" :is="item.icon" />
                            <p>
                                {{ item.name }}
                            </p>
                        </li>
                        <li
                            v-for="subMenuItem in item.subMenuItems"
                            :key="subMenuItem.routeName"
                            :class="[
                                'sub-menu-item',
                                {
                                    'sidenav-selected': isMenuItemHighlighted(
                                        subMenuItem.routeName
                                    ),
                                    'sidenav-disabled': subMenuItem.disabled,
                                },
                            ]"
                            @click="navigateOnClick(subMenuItem.routeName)"
                        >
                            <span>{{ subMenuItem.name }}</span>
                        </li>
                    </template>
                </ul>
                <ul>
                    <Label label-text="Support" />
                    <li
                        v-if="pathToPdfGuide"
                        @click="sideNavState.toggleVisible()"
                        class="sub-menu-item"
                    >
                        <AlignBoxIcon />
                        <a
                            :href="pathToPdfGuide"
                            target="_blank"
                            rel="noopener noreferrer"
                            >How-to guide</a
                        >
                    </li>
                    <li
                        @click="sideNavState.toggleVisible()"
                        class="sub-menu-item"
                    >
                        <EmailIcon />
                        <a href="mailto:heartwood@gov.bc.ca">Contact us</a>
                    </li>
                </ul>
            </div>
        </nav>
    </div>
</template>
<style lang="scss" scoped>
.fam-sidenav {
    --header-height: 3rem;
    --sidenav-width: 16rem;
    $sidenav-border: 1px solid var(--primitive-color-gray-20);

    // On mobile, the outer wrapper becomes the backdrop overlay
    @media (max-width: 1023px) {
        position: fixed;
        top: var(--header-height);
        left: 0;
        width: 100vw;
        height: calc(100vh - var(--header-height));
        background: transparent;
        pointer-events: none;
        transition: background 0.2s ease;
        z-index: 8;

        &.is-visible {
            background: rgb(0 0 0 / 35%);
            pointer-events: auto;
        }
    }

    .sidenav {
        pointer-events: auto;
        position: fixed;
        padding: 1rem 0;
        width: var(--sidenav-width);
        height: calc(100vh - var(--header-height) - env(safe-area-inset-bottom));
        padding-bottom: calc(1rem + env(safe-area-inset-bottom));
        left: 0;
        top: var(--header-height);
        overflow: hidden auto;
        background: var(--semantic-color-surface-layer-2);
        transform: translateX(-100%);
        transition: transform 0.25s ease;
        z-index: 9;
        border-right: $sidenav-border;

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

    &.is-visible .sidenav {
        transform: translateX(0);
    }

    @media (min-width: 1024px) {
        .sidenav {
            transform: translateX(0);
        }
    }
}

// For iOS Safari, the address bar is at the bottom and could block elements without this
@media (max-width: 768px) and (hover: none) and (pointer: coarse) {
    @supports (-webkit-touch-callout: none) {
        .fam-sidenav .sidenav {
            height: calc(
                100vh - 3rem - (env(safe-area-inset-bottom, 0) + 4rem)
            );
        }
    }
}
</style>
