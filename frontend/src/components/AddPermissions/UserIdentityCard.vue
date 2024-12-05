<script setup lang="ts">
import Card from "primevue/card";
import CheckMarkFilledIcon from "@carbon/icons-vue/es/checkmark--filled/16";
import type { IdimProxyBceidInfoSchema } from "fam-app-acsctl-api";

import CardColumn from "@/components/CardColumn/index.vue";
import { formatUserNameAndId } from "@/utils/UserUtils";

const props = defineProps<{
    userIdentity: IdimProxyBceidInfoSchema;
}>();
</script>

<template>
    <div class="custom-card-container user-id-card">
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
                            label="email"
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
@import "@/assets/styles/card.scss";
.user-id-card {
    margin-top: 2rem;

    svg {
        width: 1rem;
        height: 1rem;
    }
}
</style>
