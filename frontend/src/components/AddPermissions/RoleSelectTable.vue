<script setup lang="ts">
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import {
    isAbstractRoleSelected,
    type AppPermissionFormType,
} from "@/views/AddAppPermission/utils";
import { RoleType, type FamRoleDto } from "fam-admin-mgmt-api/model";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import RadioButton from "primevue/radiobutton";
import { ErrorMessage, Field, useField } from "vee-validate";
import { computed, inject, ref, type Ref } from "vue";
import ForestClientSection from "./ForestClientSection.vue";
import Label from "../UI/Label.vue";
import ConfirmDialog from "primevue/confirmdialog";
import { useConfirm } from "primevue/useconfirm";
import DelegatedAdminSection from "./DelegatedAdminSection.vue";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const confirm = useConfirm();

const props = defineProps<{
    appId: number;
    roleOptions: FamRoleDto[];
    roleFieldId: string;
    forestClientsFieldId: string;
    isDelegatedAdminOnly: boolean;
}>();

const { resetField: resetForestClientsField } = useField(
    props.forestClientsFieldId
);

/**
 * Track if a verification of a client number is in progress.
 * Disable role selection if it's verifying, otherwise a client might be added
 * right after switching.
 */
const isVerifyingClient = ref<boolean>(false);

const setIsVerifyingClient = (verifying: boolean) => {
    isVerifyingClient.value = verifying;
};

const isDelegatedAdminRowSelected = ref<boolean>(false);

const delegatedAdminRow: FamRoleDto = {
    id: -999,
    name: "delegated_admin",
    display_name: "Delegated admin",
    description:
        "Assigns and manages access for other users within their organization",
    type_code: RoleType.A,
    forest_clients: [],
};

// Rows with or without the custom row for delegated admin
const rows = computed<FamRoleDto[]>(() => {
    if (!props.isDelegatedAdminOnly) {
        return [...props.roleOptions, delegatedAdminRow];
    }
    return props.roleOptions;
});

const setRoleAndClearClients = (role: FamRoleDto) => {
    if (role.id === delegatedAdminRow.id) {
        isDelegatedAdminRowSelected.value = true;
    } else {
        isDelegatedAdminRowSelected.value = false;
        formData.value.role = role;
    }

    formData.value.forestClients = [];
    resetForestClientsField();
};

const handleRoleSelect = (role: FamRoleDto) => {
    if (formData.value.forestClients.length) {
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
                        formData.forestClients.length > 1 ? "s" : ""
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
            v-model="formData.role"
        >
            <DataTable :value="rows" class="fam-table">
                <template #empty> No role found. </template>
                <Column class="align-top-col" field="roleSelect">
                    <template #body="{ data }">
                        <RadioButton
                            :value="data"
                            :model-value="formData.role"
                            @update:model-value="handleRoleSelect"
                            :disabled="isVerifyingClient"
                        />
                    </template>
                </Column>
                <Column class="align-top-col" field="roleName" header="Role">
                    <template #body="{ data }">
                        <span>{{ data.display_name }}</span>
                    </template>
                </Column>
                <Column field="roleDescription" header="Description">
                    <template #body="{ data }">
                        <span>{{ data.description }}</span>
                        <ForestClientSection
                            v-if="
                                !isDelegatedAdminRowSelected &&
                                isAbstractRoleSelected(formData) &&
                                formData.role?.id === data.id
                            "
                            :app-id="props.appId"
                            :field-id="props.forestClientsFieldId"
                            :set-is-verifying-client="setIsVerifyingClient"
                        />
                        <DelegatedAdminSection
                            v-else-if="
                                isDelegatedAdminRowSelected &&
                                formData.role?.id === data.id
                            "
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
}
</style>
