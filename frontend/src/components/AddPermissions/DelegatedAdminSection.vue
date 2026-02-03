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
import { watch } from "vue";

const props = defineProps<{
    roleOptions: FamRoleGrantDto[];
    appId: number;
    forestClientsFieldId: string;
    formValues: AppPermissionFormType;
    setFieldValue: (field: string, value: any) => void;
    /**
     * To disable delegated admin role with 'invalid' multiple users selected.
     */
    disabled?: boolean;
}>();

const onDropdownChange = (event: DropdownChangeEvent) => {
    props.setFieldValue("role", event.value as FamRoleGrantDto);
};

watch(
    () => props.disabled,
    (isDisabled) => {
        if (isDisabled) {
            // Clear role if disabled due to invalid requirement met.
            props.setFieldValue("role", null);
        }
    }
);

</script>
<template>
    <div
        class="delegated-admin-section"
        :class="{ 'disabled-section': props.disabled }"
    >
        <NotificationMessage
            v-if="!props.disabled"
            severity="info"
            title="Note:"
            message="Delegated admin will be able to add, edit and delete users."
        />
        <NotificationMessage
            v-else
            severity="error"
            title="Note:"
            message="Delegated admin cannot be added when multiple users are selected. Please remove extra users and leave only one user to proceed."
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
            :disabled="props.formValues.forestClientInput.isVerifying || props.disabled"
        />

        <ForestClientSection
            v-if="isAbstractRoleSelected(props.formValues) && !props.disabled"
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

    &.disabled-section {
        opacity: 0.6;
        pointer-events: none;
    }

    .subsection-title-container {
        margin: 1.5rem 0;
    }
}
</style>
