<script setup lang="ts">
import Card from "primevue/card";
import Tag from "primevue/tag";
import { IconSize } from "@/enum/IconEnum";
import type { FamForestClientSchema } from "fam-app-acsctl-api";

const props = defineProps<{
    forestClientData: FamForestClientSchema[];
}>();
</script>
<template>
    <div>
        <Card class="custom-card">
            <template #header>
                <Icon icon="checkmark--filled" :size="IconSize.small" />
                <p>Verified Client Number information</p>
            </template>
            <template #content>
                <div class="w-100">
                    <div
                        v-for="client in props.forestClientData"
                        class="content-wrapper"
                    >
                        <p class="icon-wrapper">
                            <Icon
                                class="flex-grow-0 custom-carbon-icon-checkmark--filled"
                                icon="checkmark--filled"
                                :size="IconSize.small"
                                v-if="client.status?.status_code == 'A'"
                            />

                            <Icon
                                class="flex-grow-0 custom-carbon-icon-misuse"
                                icon="misuse"
                                style="margin-right: 1rem"
                                :size="IconSize.small"
                                v-else
                            />
                        </p>
                        <p
                            class="invalid"
                            v-if="!props.forestClientData"
                            style="margin-top: 0.75rem"
                        >
                            Please enter an active Forest Client Number
                        </p>

                        <p
                            class="flex-grow-0 client-id-wrapper"
                            v-if="props.forestClientData"
                        >
                            <label for="forest-client-number">
                                Client Number:
                            </label>
                            <span
                                id="forest-client-number"
                                name="forest-client-number"
                            >
                                {{ client.forest_client_number }}
                            </span>
                        </p>
                        <p
                            class="org-name-wrapper"
                            v-if="props.forestClientData"
                        >
                            <label for="forest-client-name">
                                Organization name:
                            </label>
                            <span
                                id="forest-client-name"
                                name="forest-client-name"
                                class="organization-name"
                            >
                                {{ client.client_name }}
                            </span>
                        </p>
                        <p
                            class="org-status-wrapper"
                            v-if="props.forestClientData"
                        >
                            <label for="forest-client-status" class="status">
                                Organization status:
                            </label>
                            <Tag
                                id="forest-client-status"
                                name="forest-client-status"
                                class="custom-tag"
                                :severity="
                                    client.status?.status_code == 'A'
                                        ? 'success'
                                        : 'danger'
                                "
                                :value="client.status?.description"
                            />
                        </p>
                        <Button class="btn-trash">
                            <Icon
                                id="btn-trash-can"
                                class="custom-carbon-icon--trash-can"
                                icon="trash-can"
                                :size="IconSize.small"
                                title="Remove client"
                                @click="
                                    $emit(
                                        'removeItem',
                                        client.forest_client_number
                                    )
                                "
                            />
                        </Button>
                    </div>
                </div>
            </template>
        </Card>
    </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/styles.scss";

p > label {
    margin-top: 0.25rem;
}

p {
    display: flex;
    flex-direction: column;
}

p * {
    align-self: baseline !important;
}

.content-wrapper {
    flex-direction: row !important;
    width: 100%;
    min-height: 3.25rem !important;
    align-items: center;
    justify-content: center;
}

.content-wrapper:not(:first-child) {
    border-top: $light-border-subtle-00 0.06rem solid;
    padding-top: 1rem;
}

.icon-wrapper {
    display: block;
}

.client-id-wrapper {
    margin-right: 2rem;
}

.org-name-wrapper {
    min-width: 13rem;
    margin-right: 2rem;
}

.org-status-wrapper {
    padding-top: 0.2rem;
    margin-right: 2rem;
    margin-top: 0.1rem;
}

.custom-carbon-icon-checkmark--filled,
.custom-carbon-icon-misuse,
.custom-carbon-icon--trash-can {
    margin-right: 1rem !important;
    float: left;
}

.status {
    margin-bottom: 0.6rem !important;
}

.custom-tag {
    display: inline !important;
    align-self: flex-start !important;
}

.btn-trash {
    display: block;
    padding: 0;
    border: none;
    margin-bottom: 2rem;
    max-width: 2rem;
}

.btn-trash,
.btn-trash:hover {
    background-color: transparent !important;
}
</style>
