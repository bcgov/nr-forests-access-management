<script setup lang="ts">
import Card from "primevue/card";
import CheckMarkFilledIcon from "@carbon/icons-vue/es/checkmark--filled/16";
import TrashIcon from "@carbon/icons-vue/es/trash-can/16";
import Button from "primevue/button";
import type { FamForestClientSchema } from "fam-app-acsctl-api";

import CardColumn from "@/components/CardColumn";
import Chip from "@/components/UI/Chip.vue";

defineProps<{
    forestClientData: FamForestClientSchema[];
}>();
</script>
<template>
    <div class="custom-card-container">
        <Card class="fores-client-card">
            <template #header>
                <div class="card-header">
                    <CheckMarkFilledIcon />
                    <p>Verified organization information</p>
                </div>
            </template>
            <template #content>
                <div v-for="client in forestClientData" class="client-row">
                    <div class="icon-name-wrapper medium-col">
                        <CheckMarkFilledIcon
                            v-if="client.status?.status_code == 'A'"
                        />
                        <CardColumn
                            :id="`forest-client-number-${client.forest_client_number}`"
                            label="Client number:"
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
                        <Chip
                            :label="client.status?.description ?? 'Active'"
                            color="green"
                        />
                    </CardColumn>

                    <div class="xsmall-col">
                        <Button
                            class="btn-trash"
                            @click="
                                $emit('removeItem', client.forest_client_number)
                            "
                            aria-label="Remove client"
                        >
                            <template #icon>
                                <TrashIcon />
                            </template>
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

        .xsmall-col,
        .small-col,
        .medium-col,
        .large-col {
            min-width: 5%;
            max-width: 5%;
            overflow: scroll;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: inline-block;

            p,
            span {
                overflow: scroll;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }

        .small-col {
            min-width: 15%;
            max-width: 15%;
        }

        .medium-col {
            min-width: 20%;
            max-width: 20%;
        }

        .large-col {
            min-width: 40%;
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
            p {
                margin: 0;
            }
        }
    }
}
</style>
