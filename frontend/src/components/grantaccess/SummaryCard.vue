<script setup lang="ts">
import { type PropType, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';

import { useNotificationMessage } from '@/store/NotificationState';

import type { FamUserRoleAssignmentCreate } from 'fam-api';

const props = defineProps({
    data: {
        type: Object as PropType<FamUserRoleAssignmentCreate>,
        required: true,
    },
    role_name: {
        type: String,
        required: true,
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

onMounted(() => {
    useNotificationMessage.notificationMsg =
        props.data != undefined
            ? `New access granted to ${props.data.user_name}`
            : '';
});
</script>
<template>
    <div class="row" v-if="props.data">
        <div class="col-6">
            <Card class="mb-2 p-0 p-card">
                <template #title>Summary</template>
                <template #subtitle>Review your access request</template>
                <template #content>
                    <div class="card-content">
                        <p>
                            <label>User name:&nbsp;</label>
                            <span>{{ props.data.user_name }}</span>
                        </p>
                        <p>
                            <label>Assign role:&nbsp;</label>
                            <span>{{ props.role_name }}</span>
                        </p>
                        <p v-if="props.data.forest_client_number">
                            <label>Forest Client ID:&nbsp;</label
                            ><span>
                                {{ props.data.forest_client_number }}
                            </span>
                        </p>
                        <p>
                            <label>Application:&nbsp;</label
                            ><span>{{ selectedApplicationDisplayText }} </span>
                        </p>
                    </div>
                </template>
                <template #footer>
                    <div class="card-footer">
                        <Button
                            type="submit"
                            id="grantAccessSubmit"
                            class="mb-3"
                            v-on:click="$emit('submit')"
                            :disabled="props.loading"
                        >
                            <div v-if="loading">
                                <span> Loading... </span>
                            </div>
                            <div v-else>Submit</div>
                        </Button>
                        <Button
                            class="m-3"
                            outlined
                            @click="$router.push('/grant')"
                            label="Edit Form"
                            :disabled="props.loading"
                        >
                        </Button>
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.p-button {
    width: 7.875rem;
}
.card-content {
    margin-top: 3rem;
}
.card-footer {
    margin-top: 2rem;
}
</style>
