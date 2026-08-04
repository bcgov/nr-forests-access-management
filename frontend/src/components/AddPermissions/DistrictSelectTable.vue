<script setup lang="ts">
import { AppActlApiService } from "@/services/ApiServiceFactory";
import type { AppPermissionFormType } from "@/views/AddAppPermission/utils";
import { useQuery } from "@tanstack/vue-query";
import type { FamDistrictSchema } from "fam-app-acsctl-api/model";
import Checkbox from "primevue/checkbox";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { Field, useField } from "vee-validate";
import { computed, watch } from "vue";
import ErrorText from "../UI/ErrorText.vue";
import Label from "../UI/Label.vue";
import SubsectionTitle from "../UI/SubsectionTitle.vue";

const props = defineProps<{
    fieldId: string;
    formValues: AppPermissionFormType;
    setFieldValue: (field: string, value: any) => void;
}>();

const { validate: validateDistricts, setErrors: setDistrictsError } = useField(
    props.fieldId
);

const districtsQuery = useQuery({
    queryKey: ["districts"],
    queryFn: () =>
        AppActlApiService.districtsApi.getDistricts().then((res) => res.data),
    refetchOnMount: true,
});

watch(
    () => districtsQuery.isError.value,
    (isError) => {
        if (isError) {
            setDistrictsError(
                "Failed to fetch available districts. Please try again."
            );
        }
    }
);

/**
 * Expired districts are kept out of the picker so they cannot be granted,
 * while remaining valid on permissions that already reference them.
 */
const availableDistricts = computed<FamDistrictSchema[]>(
    () => districtsQuery.data.value?.filter((d) => !d.isExpired) ?? []
);

const selectedDistricts = computed<FamDistrictSchema[]>(
    () => props.formValues.districts ?? []
);

const isDistrictSelected = (district: FamDistrictSchema) =>
    selectedDistricts.value.some(
        (selected) => selected.org_unit_code === district.org_unit_code
    );

const toggleDistrict = (district: FamDistrictSchema) => {
    const updated = [...selectedDistricts.value];
    const index = updated.findIndex(
        (selected) => selected.org_unit_code === district.org_unit_code
    );
    if (index >= 0) {
        updated.splice(index, 1);
    } else {
        updated.push(district);
    }
    props.setFieldValue("districts", updated);
    validateDistricts();
};
</script>

<template>
    <div class="district-select-table-container">
        <SubsectionTitle
            title="Restrict access by districts"
            subtitle="Select one or more districts for this access"
        />

        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            :model-value="selectedDistricts"
            @update:model-value="
                (value) => props.setFieldValue('districts', value)
            "
        >
            <Label label-text="Districts" required />

            <ErrorText v-if="errorMessage" show-icon :error-msg="errorMessage" />

            <DataTable class="fam-table" :value="availableDistricts">
                <template #empty>No district available</template>

                <Column header="">
                    <template #body="{ data }">
                        <Checkbox
                            class="fam-checkbox"
                            :binary="true"
                            :model-value="isDistrictSelected(data)"
                            @change="toggleDistrict(data)"
                        />
                    </template>
                </Column>

                <Column header="Name" field="orgUnitName" />

                <Column header="District code" field="org_unit_code" />
            </DataTable>
        </Field>
    </div>
</template>

<style lang="scss">
.district-select-table-container {
    .error-text-container {
        padding: 0;
        height: fit-content;
        margin-bottom: 0.5rem;
    }

    .subsection-title-container {
        margin: 1.5rem 0;
    }

    .fam-table {
        .p-datatable-emptymessage {
            background-color: var(--semantic-color-surface-layer-1);
        }
    }

    .fam-checkbox {
        display: flex;
        flex-direction: row;
        align-items: center;
        .p-checkbox-box {
            width: 1rem;
            height: 1rem;
        }
    }
}
</style>
