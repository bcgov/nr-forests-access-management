<script setup lang="ts">
import Card from 'primevue/card';
import type { PropType } from 'vue';
import type { FamForestClientStatus } from 'fam-api/dist/model/fam-forest-client-status';

const props = defineProps({
    status: {
        type: Object as PropType<FamForestClientStatus>,
        required: true,
        default: {
            description: "Doesn't exist",
        },
    },
    text: {
        type: String,
        required: true,
        default: '',
    },
});
</script>
<template>
    <div>
        <Card class="mb-2 p-0">
            <template #content>
                <div class="row">
                    <p>
                        <label>Organization status: </label>&nbsp;<Tag
                            :text="props.status.description"
                            :active="props.status.status_code === 'A'"
                        />
                    </p>
                </div>
                <div
                    v-if="props.status.description != 'Doesn\'t exist'"
                    class="row"
                >
                    <p>
                        <label>Organization name: </label>&nbsp;<span
                            class="organization-name"
                            >{{ props.text }}</span
                        >
                    </p>
                </div>
                <span class="invalid" v-if="props.status.status_code !== 'A'"
                    >Please enter an active Forest Client ID</span
                >
            </template>
        </Card>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
p {
    margin: 0;
    padding: 0 !important;
    display: inline-flex;
}

p > label {
    margin-top: 4px;
}
.invalid {
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #dc3545;
}
.organization-name {
    font-size: 18px;
    line-height: 28px;
}
</style>
