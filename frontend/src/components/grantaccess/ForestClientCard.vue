<script setup lang="ts">
import Card from "primevue/card";
import Tag from "primevue/tag";
import Button from "primevue/button";
import Icon from "@/components/common/Icon.vue";
import { IconSize } from "@/enum/IconEnum";
import type { FamForestClientSchema } from "fam-app-acsctl-api";

import CardTextCol from "@/components/CardTextCol";

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
                    <p class="icon-wrapper">
                        <Icon
                            class="custom-carbon-icon-checkmark--filled"
                            icon="checkmark--filled"
                            :size="IconSize.small"
                            v-if="client.status?.status_code == 'A'"
                        />

                        <Icon
                            class="custom-carbon-icon-misuse"
                            icon="misuse"
                            style="margin-right: 1rem"
                            :size="IconSize.small"
                            v-else
                        />
                    </p>

                    <CardTextCol
                        :id="`forest-client-number-${client.forest_client_number}`"
                        label="Client Number:"
                        :description="client.forest_client_number"
                    />

                    <CardTextCol
                        :id="`forest-client-name-${client.forest_client_number}`"
                        label="Organization name:"
                        :description="client.client_name"
                    />

                    <CardTextCol
                        :id="`forest-client-status-${client.forest_client_number}`"
                        label="Organization status:"
                        hide-description
                    >
                        <Tag
                            name="forest-client-status"
                            :severity="
                                client.status?.status_code == 'A'
                                    ? 'success'
                                    : 'danger'
                            "
                            :value="client.status?.description"
                        />
                    </CardTextCol>

                    <Button class="btn-trash">
                        <Icon
                            id="btn-trash-can"
                            class="custom-carbon-icon--trash-can"
                            icon="trash-can"
                            :size="IconSize.small"
                            title="Remove client"
                            @click="
                                $emit('removeItem', client.forest_client_number)
                            "
                        />
                    </Button>
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
        .btn-trash {
            display: block;
            padding: 0;
            border: none;
            margin-bottom: 2rem;
            max-width: 2rem;
        }

        .btn-trash,
        .btn-trash:hover {
            background-color: transparent;
        }
    }
}
</style>
