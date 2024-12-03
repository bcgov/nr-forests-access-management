<script setup lang="ts">
import { inject, type Ref } from "vue";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import {
    isAbstractRoleSelected,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import NotificationMessage from "../UI/NotificationMessage.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import Dropdown from "../UI/Dropdown.vue";
import type { DropdownChangeEvent } from "primevue/dropdown";
import ForestClientSection from "./ForestClientSection.vue";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const props = defineProps<{
    roleOptions: FamRoleDto[];
    appId: number;
    forestClientsFieldId: string;
}>();

const onDropdownChange = (event: DropdownChangeEvent) => {
    formData.value.role = event.value as FamRoleDto;
};
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

        <Dropdown
            class="delegated-admin-role-dropdown"
            required
            name="role"
            label-text="Role"
            :value="formData.role"
            :options="props.roleOptions"
            option-label="display_name"
            :on-change="onDropdownChange"
            :disabled="formData.forestClientInput.isVerifying"
        />

        <ForestClientSection
            v-if="isAbstractRoleSelected(formData)"
            :app-id="props.appId"
            :field-id="props.forestClientsFieldId"
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
