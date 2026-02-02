<script setup lang="ts">
import {
    isAbstractRoleSelected,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import type { FamRoleGrantDto } from "fam-admin-mgmt-api/model";
import type { DropdownChangeEvent } from "primevue/dropdown";
import Dropdown from "../UI/Dropdown.vue";
import NotificationMessage from "../UI/NotificationMessage.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";
import ForestClientSection from "./ForestClientAddTable.vue";

const props = defineProps<{
    roleOptions: FamRoleGrantDto[];
    appId: number;
    forestClientsFieldId: string;
    formValues: AppPermissionFormType;
    setFieldValue: (field: string, value: any) => void;
}>();

const onDropdownChange = (event: DropdownChangeEvent) => {
    props.setFieldValue("role", event.value as FamRoleGrantDto);
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
            :value="props.formValues.role"
            :options="props.roleOptions"
            option-label="display_name"
            :on-change="onDropdownChange"
            :disabled="props.formValues.forestClientInput.isVerifying"
        />

        <ForestClientSection
            v-if="isAbstractRoleSelected(props.formValues)"
            :app-id="props.appId"
            :field-id="props.forestClientsFieldId"
            :form-values="props.formValues"
            :set-field-value="props.setFieldValue"
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
