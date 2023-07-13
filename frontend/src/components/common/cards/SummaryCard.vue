<script setup lang="ts">
import { ref, type PropType } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import type { FamUserRoleAssignmentCreate } from 'fam-api';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';

const selected = ref('');
const props = defineProps({
    data: {
        type: Object as PropType<FamUserRoleAssignmentCreate>,
        required: true,
    },
});
</script>
<template>
    <div class="row">
        <div class="col-6">
            <Card class="mb-2 p-0 p-card">
                <template #title>Summary</template>
                <template #subtitle>Review your access request</template>
                <template #content>
                    <div class="card-content">
                        <p>
                            <label>User name:&nbsp;</label
                            ><span>{{ props.data.user_name }}</span>
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
                            label="Submit"
                            v-on:click="$emit('submit')"
                        ></Button>
                        <Button
                            class="m-3"
                            outlined
                            @click="$router.push('/grant')"
                            label="Edit Form"
                        ></Button>
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
.p-button {
    width: 126px;
}
.card-content {
    margin-top: 48px;
}
.card-footer {
    margin-top: 34px;
}
</style>
