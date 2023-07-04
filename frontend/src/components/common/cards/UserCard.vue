<template>
    <div>
        <Card class="mb-2 p-0 p-card">
            <template class="py-0" #content>
                <div class="row py-0">
                    <p style="margin: 0">
                        <label>Name: </label><span>&nbsp;{{ props.name }}</span>
                    </p>
                </div>
                <div v-if="props.status" class="row py-0">
                    <p style="margin: 0">
                        <label>Organization: </label
                        ><span>&nbsp;{{ props.organization }}</span>
                    </p>
                </div>
                <!-- <span class="invalid" v-if="props.status.status_code !== 'A'"
                    >Cannot find user</span
                > -->
            </template>
        </Card>
    </div>
</template>

<script setup lang="ts">
import type { FamForestClientStatus } from 'fam-api/dist/model/fam-forest-client-status';
import { ref, type PropType } from 'vue';
import Card from 'primevue/card';

const selected = ref('');
const props = defineProps({
    status: {
        type: Object as PropType<FamForestClientStatus>,
        required: true,
        default: {
            description: "Doesn't exist",
        },
    },
    name: {
        type: String,
        required: true,
        default: '',
    },
    organization: {
        type: String,
        required: true,
        default: '',
    },
});
</script>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';

p {
    margin: 0 !important;
    padding: 0 !important;
}

.invalid {
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #dc3545;
}
.organization-name {
    font-style: normal;
    font-weight: 400;
    font-size: 18px;
    line-height: 28px;
}
</style>
