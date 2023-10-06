<script setup lang="ts">
import Button from '@/components/common/Button.vue';
import { selectedApplicationDisplayText } from '@/store/ApplicationState';
import Card from 'primevue/card';
import type { PropType } from 'vue';

import LoadingState from '@/store/LoadingState';
import type { FamUserRoleAssignment } from '@/store/GrantAccessDataState';

const props = defineProps({
    data: {
        type: Object as PropType<FamUserRoleAssignment>,
        required: true,
    },
    role_name: {
        type: String,
        required: true,
    },
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
                        <p
                            v-if="
                                props.data.forest_client_number_list.length > 0
                            "
                        >
                            <label>Forest Client ID:&nbsp;</label
                            ><span
                                v-for="(forest_number, index) in props.data
                                    .forest_client_number_list"
                            >
                                {{
                                    `${forest_number.forest_client_number}${
                                        index <
                                        props.data.forest_client_number_list
                                            .length -
                                            1
                                            ? ', '
                                            : ''
                                    }`
                                }}
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
                            :name="'grantAccessSubmit'"
                            class="mb-3"
                            aria-label="Submit form"
                            :label="'Submit'"
                            :loading-label="'Submitting...'"
                            v-on:click="$emit('submit')"
                            :disabled="LoadingState.isLoading.value"
                        >
                        </Button>
                        <Button
                            class="m-3"
                            outlined
                            @click="$router.push('/grant')"
                            label="Edit Form"
                            :disabled="LoadingState.isLoading.value"
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
