<script setup lang="ts">
import Card from "primevue/card";
import CheckMarkFilledIcon from "@carbon/icons-vue/es/checkmark--filled/16";
import ErrorIcon from "@carbon/icons-vue/es/misuse/16";
import type { IdimProxyBceidInfoSchema } from "fam-app-acsctl-api";

import CardColumn from "@/components/CardColumn/index.vue";

const props = defineProps<{
    userIdentity: IdimProxyBceidInfoSchema;
    errorMsg: string;
}>();
</script>

<template>
    <div class="custom-card-container user-id-card">
        <Card>
            <template #header>
                <CheckMarkFilledIcon v-if="props.userIdentity.found" />
                <ErrorIcon class="error-icon" v-else />
                <p>Verified user information</p>
            </template>

            <template #content v-if="!props.errorMsg">
                <CardColumn
                    :id="`user-card-id-${props.userIdentity.userId}`"
                    label="Username"
                    :description="props.userIdentity.userId"
                />
                <CardColumn
                    v-if="props.userIdentity.found"
                    :id="`user-card-first-name-${props.userIdentity.userId}`"
                    label="First Name"
                    :description="props.userIdentity.firstName"
                />
                <CardColumn
                    v-if="props.userIdentity.found"
                    :id="`user-card-last-name-${props.userIdentity.userId}`"
                    label="Last Name"
                    :description="props.userIdentity.lastName"
                />
                <CardColumn
                    v-if="props.userIdentity.found && props.userIdentity.email"
                    :id="`user-card-email-${props.userIdentity.userId}`"
                    label="email"
                    :description="props.userIdentity.email"
                />
                <CardColumn
                    v-if="
                        props.userIdentity.found &&
                        props.userIdentity.businessLegalName
                    "
                    :id="`user-card-org-name-${props.userIdentity.userId}`"
                    label="Organization Name"
                    :description="props.userIdentity.businessLegalName"
                />
                <div v-if="!props.userIdentity.found" class="invalid">
                    User does not exist
                </div>
            </template>
            <template #content v-else-if="props.errorMsg">
                <div>props.errorMsg</div>
            </template>
        </Card>
    </div>
</template>

<style lang="scss">
@import "@/assets/styles/card.scss";
.user-id-card {
    margin-top: 2rem;
    width: 100%;
    min-width: fit-content;

    .p-card-content {
        display: flex;
        flex-direction: row;
        gap: 2rem;
    }
}
</style>
