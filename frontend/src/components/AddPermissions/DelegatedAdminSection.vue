<script setup lang="ts">
import { inject, type Ref } from "vue";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import type { AppPermissionFormType } from "@/views/AddAppPermission/utils";
import NotificationMessage from "../UI/NotificationMessage.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}
</script>
<template>
    <div class="delegated-admin-section">
        <NotificationMessage
            severity="info"
            title="Note:"
            message="Delegated admin will be able to add, edit and delete users."
        />

        <SubsectionTitle
            title="Role the delegated admin can assign"
            subtitle="Select the role the user can assign to others"
        />
    </div>
</template>
<style lang="scss">
.delegated-admin-section {
    margin-top: 1.5rem;

    .subsection-title-container {
        margin: 1.5rem 0;
    }
}
</style>
