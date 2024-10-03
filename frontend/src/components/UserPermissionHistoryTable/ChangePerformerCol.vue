<script setup lang="ts">
import UserAvatar16 from '@carbon/icons-vue/es/user--avatar/16';
import { formatUserNameAndId } from '@/utils/UserUtils';
import type { PrivilegeChangePerformerSchema } from 'fam-app-acsctl-api/model';

defineProps<{
    performerDetails: PrivilegeChangePerformerSchema;
}>();

</script>

<template>
    <div class="change-performer-col-container">
        <div class="icon-container">
            <UserAvatar16 />
        </div>
        <div class="user-detail-container">
            <p>
                {{
                    formatUserNameAndId(
                        performerDetails.username,
                        performerDetails.first_name,
                        performerDetails.last_name
                    )
                }}
            </p>
            <p v-if="performerDetails.email">
                {{ performerDetails.email }}
            </p>

        </div>
    </div>
</template>

<style lang="scss">
.change-performer-col-container {
    display: flex;
    flex-direction: row;

    .icon-container {
        margin-right: 0.25rem;
        display: flex;
        align-items: flex-start;

        svg {
            width: 1.25rem;
            height: 1.25rem;
        }
    }
}
</style>
