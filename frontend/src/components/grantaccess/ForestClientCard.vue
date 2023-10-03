<script setup lang="ts">
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import { IconSize } from '@/enum/IconEnum';
import type { PropType } from 'vue';
import type { FamForestClient } from 'fam-api/dist/model/fam-forest-client';

const props = defineProps({
    forestClientData: {
        type: Object as PropType<FamForestClient>,
    },
});
</script>
<template>
    <!-- temporary condition until invalid input handling is implemented -->
    <div>
        <Card class="custom-card">
            <template #header>
                <Icon
                    icon="checkmark--filled"
                    :size="IconSize.small"
                    v-if="props.forestClientData?.status?.status_code == 'A'"
                />
                <Icon
                    class="custom-carbon-icon-error--filled"
                    icon="error--filled"
                    :size="IconSize.small"
                    v-else
                />
                <p>Verified Client ID information</p>
            </template>
            <template #content>
                <div class="w-100">
                    <div class="content-wrapper">
                        <Icon
                            class="row flex-grow-0 custom-carbon-icon-checkmark--filled"
                            icon="checkmark--filled"
                            :size="IconSize.small"
                            v-if="
                                props.forestClientData?.status?.status_code ==
                                'A'
                            "
                        />

                        <Icon
                            class="row flex-grow-0 custom-carbon-icon-error--filled"
                            icon="error--filled"
                            style="margin-right: 1rem"
                            :size="IconSize.small"
                            v-else
                        />
                        <p
                            class="invalid col"
                            v-if="!props.forestClientData"
                            style="margin-top: 0.75rem"
                        >
                            Please enter an active Forest Client ID
                        </p>

                        <p
                            class="col flex-grow-0 client-id-wrapper"
                            v-if="props.forestClientData"
                        >
                            <label class="col">Client ID: </label>
                            <span class="col">
                                {{
                                    props.forestClientData?.forest_client_number
                                }}
                            </span>
                        </p>
                        <p class="col" v-if="props.forestClientData">
                            <label class="row">Organization name: </label>
                            <span class="organization-name row">
                                {{ props.forestClientData?.client_name }}
                            </span>
                        </p>
                        <p
                            class="col org-status-wrapper"
                            v-if="props.forestClientData"
                        >
                            <label class="row status"
                                >Organization status:
                            </label>
                            <Tag
                                class="custom-tag"
                                :severity="
                                    props.forestClientData?.status
                                        ?.status_code == 'A'
                                        ? 'success'
                                        : 'danger'
                                "
                                :value="
                                    props.forestClientData?.status?.description
                                "
                            />
                        </p>

                        <!-- hidden until functionaly arrives -->
                        <!-- <Button class="btn-trash">
                            <Icon
                                class="row custom-carbon-icon--trash-can"
                                icon="trash-can"
                                :size="IconSize.small"
                                title="Remove client"
                            />
                        </Button> -->
                    </div>
                </div>
            </template>
        </Card>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

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

.col {
    align-self: center;
}

.content-wrapper {
    flex-direction: row !important;
    width: 100%;
}

.content-wrapper:not(:first-child) {
    border-top: $light-border-subtle-00 0.06rem solid;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
}

.client-id-wrapper {
    margin-right: 3rem;
}

.custom-carbon-icon-checkmark--filled {
    margin-right: 1rem !important;
}

.org-status-wrapper {
    margin-top: 0.1rem;
}
.status {
    margin-bottom: 0.6rem !important;
}

.custom-tag {
    display: inline !important;
    align-self: flex-start !important;
}

.btn-trash {
    padding: 0;
    border: none;
    margin-bottom: 1.5rem;
}

.btn-trash,
.btn-trash:hover {
    background-color: transparent !important;
}
</style>
