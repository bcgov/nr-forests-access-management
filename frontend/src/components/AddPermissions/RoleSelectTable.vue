<script setup lang="ts">
import {
    isAbstractRoleSelected,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import { RoleType, type FamRoleGrantDto } from "fam-admin-mgmt-api/model";
import Column from "primevue/column";
import ConfirmDialog from "primevue/confirmdialog";
import DataTable from "primevue/datatable";
import RadioButton from "primevue/radiobutton";
import { useConfirm } from "primevue/useconfirm";
import { ErrorMessage, Field } from "vee-validate";
import { computed, ref } from "vue";
import Label from "../UI/Label.vue";
import DelegatedAdminSection from "./DelegatedAdminSection.vue";
import ForestClientAddTable from "./ForestClientAddTable.vue";
import ForestClientSelectTable from "./ForestClientSelectTable.vue";

const props = defineProps<{
    appId: number;
    roleOptions: FamRoleGrantDto[];
    roleFieldId: string;
    forestClientsFieldId: string;
    /**
     * Determines whether the logged in user is only a d-admin and not an app admin
     */
    isDelegatedAdminOnly: boolean;
    setFieldValue: (field: string, value: any) => void;
    formValues: AppPermissionFormType;
}>();

/**
 * Checks if attempting to switch to delegated admin role with multiple users selected.
 * When true, DelegatedAdminSection should be disabled pending user cleanup.
 */
const isAttemptingDelegatedAdminWithMultipleUsers = computed(() => {
    const isDelegatedAdminSelected = selectedRole.value?.id === delegatedAdminRow.id;
    const hasMultipleUsers = props.formValues.users.length > 1;
    return isDelegatedAdminSelected && hasMultipleUsers;
});


const confirm = useConfirm();

/**
 * An intermediate value to accommodate the fake delegated admin role.
 */
const selectedRole = ref<FamRoleGrantDto | null>(props.formValues.role);

/**
 * A fake d-admin row data for display purpose in the role table.
 */
const delegatedAdminRow: FamRoleGrantDto = {
    id: -999,
    name: "delegated_admin",
    display_name: "Delegated admin",
    description:
        "Assigns and manages access for other users within their organization",
    type_code: RoleType.A,
    forest_clients: [],
};

// Rows with or without the custom row for delegated admin
const rows = computed<FamRoleGrantDto[]>(() => {
    if (!props.isDelegatedAdminOnly) {
        return [...props.roleOptions, delegatedAdminRow];
    }
    return props.roleOptions;
});

/**
 * Sets the role selectedRole then formData accordingly.
 */
const setRoleAndClearClients = (role: FamRoleGrantDto) => {
    if (role.id === delegatedAdminRow.id) {
        selectedRole.value = role;
        props.setFieldValue('role', null);
        props.setFieldValue('isAddingDelegatedAdmin', true);
    } else {
        selectedRole.value = role;
        props.setFieldValue('role', role);
        props.setFieldValue('isAddingDelegatedAdmin', false);
    }

    props.setFieldValue('forestClients', []);
    props.setFieldValue('forestClientInput', {
        ...props.formValues.forestClientInput,
        value: '',
        isValid: true,
        errorMsg: '',
    });
};

const handleRoleSelect = (role: FamRoleGrantDto) => {
    if ((props.formValues.forestClients?.length ?? 0) > 0) {
        confirm.require({
            group: "changeRole",
            header: "Changing Role",
            rejectLabel: "Cancel",
            acceptLabel: "Continue",
            acceptClass: "dialog-accept-button",
            accept: () => setRoleAndClearClients(role),
        });
    } else {
        setRoleAndClearClients(role);
    }
};
</script>

<template>
    <div class="role-select-table-container">
        <ConfirmDialog
            class="confirm-dialog-with-blue-button"
            group="changeRole"
        >
            <template #message>
                <p>
                    Changing the role will remove the associated organization{{
                        props.formValues.forestClients.length > 1 ? "s" : ""
                    }}. Are you sure you want to continue?
                </p>
            </template>
        </ConfirmDialog>
        <Label :for="props.roleFieldId" label-text="Role" required />

        <ErrorMessage
            class="table-error invalid-feedback"
            :name="props.roleFieldId"
        />
        <!-- Field validation with v-model bound to computedRole -->
        <Field
            :name="props.roleFieldId"
            aria-label="Role Select"
            v-model="props.formValues.role"
        >
            <DataTable :value="rows" class="fam-table">
                <template #empty> No role found. </template>
                <Column class="align-top-col" field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton
                            :value="data"
                            :model-value="selectedRole"
                            @update:model-value="handleRoleSelect"
                            :disabled="props.formValues.forestClientInput.isVerifying"
                        />
                    </template>
                </Column>
                <Column class="align-top-col" field="roleName" header="Role">
                    <template #body="{ data }">
                        <span class="role-display-name">{{
                            data.display_name
                        }}</span>
                    </template>
                </Column>
                <Column field="roleDescription" header="Description">
                    <template #body="{ data }">
                        <span>{{ data.description }}</span>
                        <ForestClientSelectTable
                            v-if="
                                isDelegatedAdminOnly &&
                                isAbstractRoleSelected(props.formValues) &&
                                props.formValues.role?.id === data.id
                            "
                            :app-id="props.appId"
                            :field-id="props.forestClientsFieldId"
                        />

                        <ForestClientAddTable
                            v-else-if="
                                selectedRole?.id !== delegatedAdminRow.id &&
                                isAbstractRoleSelected(props.formValues) &&
                                props.formValues.role?.id === data.id
                            "
                            :app-id="props.appId"
                            :field-id="props.forestClientsFieldId"
                            :form-values="props.formValues"
                            :set-field-value="props.setFieldValue"
                        />

                        <DelegatedAdminSection
                            v-else-if="
                                selectedRole?.id === delegatedAdminRow.id &&
                                selectedRole?.id === data.id
                            "
                            :role-options="props.roleOptions"
                            :app-id="props.appId"
                            :forest-clients-field-id="props.forestClientsFieldId"
                            :form-values="props.formValues"
                            :set-field-value="props.setFieldValue"
                            :disabled="isAttemptingDelegatedAdminWithMultipleUsers"
                        />
                    </template>
                </Column>
            </DataTable>
        </Field>
    </div>
</template>
<style lang="scss">
.role-select-table-container {
    margin-top: 2.5rem;

    td.align-top-col {
        vertical-align: top;
    }

    .p-datatable {
        .p-datatable-tbody > tr:hover {
            background-color: colors.$white;
        }
    }

    .table-error {
        display: block;
    }

    .role-display-name {
        white-space: nowrap;
    }
}
</style>
