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

/**
 * TODO:
 * There are several child-component from `frontend/src/views/AddAppPermission/index.vue`, this `DelegatedAdminSection.vue`
 * is one of them. Previously this child-component inject a parent form directly for direct field manipulation, which is too
 * much coupling and now when using a recommended vee-validate library's Composition API `useForm`, the parent form now is
 * following a best practice to be a "read-only form". So the child-component can't directly change the values dynamically
 * anymore. The 'formValues' and 'setFieldValue' are new addition of props passed in from parent component, to overcome
 * previous coupling of parent form in the child component. They are provided from vee-validate's 'useForm' API.
 *
 * This is a temporary solution agreed after discussion with Olga. Later, we will change delegated-admin granting
 * permission backend to handle multiple users as well. That time we will totally refactor all child components to be
 * only accepting necessary props from parent fields' value only, not the form itself, and provide "event" based
 * callback for parent component to handle the value change from child component, instead of child component directly
 * manipulate parent form values.
 */
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
    props.setFieldValue('forestClients', []);
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
            message="Delegated Admin can only be assigned to one user at a time. Select a single user to continue."
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
