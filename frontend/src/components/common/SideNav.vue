<script setup lang="ts">
import { sideNavState } from "@/store/SideNavState";
import Sidebar from "primevue/sidebar";
import type { PropType } from "vue";
import { hashRouter } from "@/router";

export interface ISideNavItem {
    name: string;
    icon: string;
    link: string;
    disabled: boolean;
    childLinks?: string[];
    items?: [ISideNavItem];
}

const props = defineProps({
    data: {
        type: Object as PropType<ISideNavItem[]>,
        required: true,
        default: "",
    },
});
</script>
<template>
    <Sidebar v-model:visible="sideNavState.isVisible">
        <nav class="sidenav">
            <div class="content">
                <ul>
                    <template v-for="item in props.data">
                        <li
                            class="header"
                            :class="{
                                'sidenav-selected':
                                    $router.currentRoute.value.path ==
                                        item.link ||
                                    item.childLinks?.find((child) =>
                                        $router.currentRoute.value.path.includes(
                                            child
                                        )
                                    ),
                                'sidenav-disabled': item.disabled,
                            }"
                            @click="hashRouter.push(item.link)"
                        >
                            {{ item.name }}
                        </li>
                        <li
                            class="child"
                            v-for="child in item.items"
                            :class="{
                                'sidenav-selected':
                                    $router.currentRoute.value.path ==
                                    child.link,
                                'sidenav-disabled': child.disabled,
                            }"
                            @click="hashRouter.push(child.link)"
                        >
                            <span>{{ child.name }}</span>
                        </li>
                    </template>
                </ul>
            </div>

            <!-- Leaving this piece of code below commented out because we will need to reuse it again in the future when we have the functionality -->
            <!-- <div class="support-section sidenav-disabled">
                <ul>
                    <li class="header">Support</li>
                    <ul>
                        <li
                            class="child"
                            click="mailto:SIBIFSAF@Victoria1.gov.bc.ca"
                        >
                            <Icon
                                icon="help"
                                :size="IconSize.small"
                                class="custom-carbon-icon--help"
                            />
                            Need help?
                        </li>
                    </ul>
                </ul>
            </div> -->
        </nav>
    </Sidebar>
</template>
<style lang="scss" scoped>
@import "@/assets/styles/styles.scss";

.sidenav {
    position: fixed;
    padding: 2.25rem 0rem;
    width: 100%;
    height: calc(100vh - 3.125rem);
    left: 0rem;
    overflow-x: hidden;
    overflow-y: auto;

    .content {
        position: relative;
        min-height: auto;
    }

    .support-section {
        position: absolute;
        bottom: 0rem;
    }
}

.sidenav ul {
    padding: 0;
    margin: 0;
    list-style-type: none;
}

.sidenav li {
    @extend %helper-text-01;
    color: $light-text-secondary;
    font-size: 1rem;
    font-weight: 400;
    align-items: center;
    padding: 0.9375rem 1rem;

    i {
        vertical-align: middle;
    }

    a {
        text-decoration: none;
    }
}

.sidenav li.child > span {
    margin-left: 1.5rem;
}

.sidenav li.child:hover,
li.header:hover {
    background: $light-layer-hover-01;
    color: $light-text-primary;
    cursor: pointer;
}

.sidenav-disabled {
    display: none;
}

.sidenav-selected {
    background: $light-layer-selected-01;
    box-shadow: inset 0.188rem 0rem 0rem $light-border-interactive;
    color: $light-text-primary !important;
    font-weight: 700 !important;
    cursor: pointer;
}

.sidenav-selected:hover {
    background: $light-layer-selected-hover-01 !important;
}

@media (min-width: 768px) {
    .sidenav {
        width: 100%;
    }
}
</style>
