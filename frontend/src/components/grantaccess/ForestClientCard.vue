<script setup lang="ts">
import Card from "primevue/card";
import Tag from "primevue/tag";
import Button from "primevue/button";
import Icon from "@/components/common/Icon.vue";
import { IconSize } from "@/enum/IconEnum";
import type { FamForestClientSchema } from "fam-app-acsctl-api";

import CardColumn from "@/components/CardColumn";

defineProps<{
    forestClientData: FamForestClientSchema[];
}>();
</script>
<template>
    <div class="custom-card-container">
        <Card class="fores-client-card">
            <template #header>
                <div class="card-header">
                    <Icon icon="checkmark--filled" :size="IconSize.small" />
                    <p>Verified Client Number information</p>
                </div>
            </template>
            <template #content>
                <div v-for="client in forestClientData" class="client-row">
                    <div class="icon-name-wrapper medium-col">
                        <Icon
                            class="custom-carbon-icon-checkmark--filled"
                            icon="checkmark--filled"
                            :size="IconSize.small"
                            v-if="client.status?.status_code == 'A'"
                        />
                        <CardColumn
                            :id="`forest-client-number-${client.forest_client_number}`"
                            label="Client Number:"
                            :description="client.forest_client_number"
                        />
                    </div>

                    <CardColumn
                        class="large-col"
                        :id="`forest-client-name-${client.forest_client_number}`"
                        label="Name:"
                        :description="client.client_name"
                    />

                    <CardColumn
                        class="small-col"
                        :id="`forest-client-status-${client.forest_client_number}`"
                        label="Status:"
                        hide-description
                    >
                        <Tag
                            class="forest-client-status-tag"
                            name="forest-client-status"
                            :severity="
                                client.status?.status_code == 'A'
                                    ? 'success'
                                    : 'danger'
                            "
                            :value="client.status?.description"
                        />
                    </CardColumn>

                    <div class="small-col">
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
.fores-client-card {
    display: flex;
    flex-direction: column;

    .client-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        gap: 2rem;

        margin-bottom: 1.5rem;

        &:last-child {
            margin-bottom: 0; // Remove gap after the last row
        }

        .small-col {
            flex: 0 0 10%; // Fixed width for small columns
            max-width: 10%;
        }

        .medium-col {
            flex: 0 0 20%; // Fixed width for medium columns
            max-width: 20%;
        }

        .large-col {
            flex: 0 0 40%; // Fixed width for large columns
            max-width: 40%;
        }

        .icon-name-wrapper {
            display: flex;
            flex-direction: row;
            align-items: center;
            svg {
                margin-right: 1rem;
            }
        }

        .btn-trash {
            display: block;
            padding: 0;
            border: none;
            width: 2rem;
        }

        .btn-trash,
        .btn-trash:hover {
            background-color: transparent;
        }

        .forest-client-status-tag {
            width: fit-content;
        }
    }
}
</style>
