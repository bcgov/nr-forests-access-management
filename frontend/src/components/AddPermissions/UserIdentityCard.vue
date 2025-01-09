<script setup lang="ts">
import CheckMarkFilledIcon from "@carbon/icons-vue/es/checkmark--filled/16";
import type { IdimProxyBceidInfoSchema } from "fam-app-acsctl-api";
import Card from "primevue/card";

import CardColumn from "@/components/CardColumn/index.vue";
import { formatUserNameAndId } from "@/utils/UserUtils";

const props = defineProps<{
    userIdentity: IdimProxyBceidInfoSchema;
}>();
</script>

<template>
    <div class="user-id-card">
        <Card>
            <template #header>
                <CheckMarkFilledIcon />
                <p>Verified user information</p>
            </template>

            <template #content>
                <div class="container-fluid">
                    <div class="row gy-4">
                        <CardColumn
                            :id="`user-card-id-${props.userIdentity.userId}`"
                            label="Username"
                            :description="props.userIdentity.userId"
                            class="col-auto"
                        />
                        <CardColumn
                            v-if="props.userIdentity.found"
                            :id="`user-card-full-name-${props.userIdentity.userId}`"
                            label="Full Name"
                            :description="
                                formatUserNameAndId(
                                    null,
                                    props.userIdentity.firstName,
                                    props.userIdentity.lastName
                                )
                            "
                            class="col-auto"
                        />
                        <CardColumn
                            v-if="
                                props.userIdentity.found &&
                                props.userIdentity.email
                            "
                            :id="`user-card-email-${props.userIdentity.userId}`"
                            label="Email"
                            :description="props.userIdentity.email"
                            class="col-auto"
                        />
                        <CardColumn
                            v-if="
                                props.userIdentity.found &&
                                props.userIdentity.businessLegalName
                            "
                            :id="`user-card-org-name-${props.userIdentity.userId}`"
                            label="Organization Name"
                            :description="props.userIdentity.businessLegalName"
                            class="col-auto"
                        />
                    </div>
                </div>
            </template>
        </Card>
    </div>
</template>

<style lang="scss">
.user-id-card {
    margin-top: 2rem;

    .p-card {
        .p-card-header {
            display: flex;
            padding: 1.5rem;
            align-items: center;

            svg {
                width: 1rem;
                height: 1rem;
                color: var(--support-success);
                margin-bottom: 0.1rem;
            }

            p {
                @include type.type-style("heading-compact-01");
                margin: 0;
                padding: 0 0 0 1rem;
                margin-bottom: 0;
                color: var(--text-primary);
            }
        }

        .custom-carbon-icon-misuse {
            fill: var(--support-error);
        }
    }
}
</style>
