<template>
    <div>
        <b-card class="mb-2">
            <b-card-text>
                <Tag
                    :text="props.status.description"
                    :active="props.status.status_code === 'A' ? true : false"
                />
                <span class="organization-name">{{ props.text }}</span
                ><br />
                <span class="invalid" v-if="props.status.status_code !== 'A'"
                    >Please enter an active Forest Client ID</span
                >
            </b-card-text>
        </b-card>
    </div>
</template>

<script setup lang="ts">
import type { FamForestClientStatus } from 'fam-api/dist/model/fam-forest-client-status';
import { ref, type PropType } from 'vue';

const selected = ref('');
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

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

.invalid {
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #dc3545;
}
.organization-name {
    font-style: normal;
    font-weight: 400;
    font-size: 20px;
    line-height: 28px;
}
</style>
