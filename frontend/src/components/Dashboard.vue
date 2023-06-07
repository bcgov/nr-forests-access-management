<script setup lang="ts">
import authService from '@/services/AuthService';
import Button from 'primevue/button';
import Seeding from '../assets/images/seeding.png';
import logo from '../assets/images/bc-gov-logo.png';
import Dropdown from 'primevue/dropdown';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import { computed, onMounted, ref } from 'vue';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
} from '@/store/ApplicationState';
import router from '@/router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup'; // optional
import Row from 'primevue/row'; // optional
import { FilterMatchMode } from 'primevue/api';
const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();
const loading = ref<boolean>(false);
const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    name: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    'country.name': { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    representative: { value: null, matchMode: FilterMatchMode.IN },
    status: { value: null, matchMode: FilterMatchMode.EQUALS },
    verified: { value: null, matchMode: FilterMatchMode.EQUALS },
});
onMounted(async () => {
    // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
    try {
        applicationsUserAdministers.value = (
            await applicationsApi.getApplications()
        ).data;
        // If user can only manage one application redirect to manage access screen
        if (applicationsUserAdministers.value.length == 1) {
            selectedApplication.value = applicationsUserAdministers.value[0];
            router.push('/manage');
        }
    } catch (error: any) {
        return Promise.reject(error);
    }
});
const filteredOptions = computed(() => {
    return applicationsUserAdministers.value;
});
</script>

<template>
    <div class="container vh-100">
        <h1>Dashboard</h1>
        <div class="row h-25">
            <div class="col-sm-12 col-md-12 col-lg-12">
                <form id="selectApplicationForm" class="form-container">
                    <div class="form-group col-md-5">
                        <label
                            >You are modifying access in this
                            application:</label
                        >
                        <Dropdown
                            v-model="selectedApplication"
                            :options="filteredOptions"
                            optionLabel="name"
                            placeholder="Choose an option"
                            class="application-dropdown"
                        />
                    </div>
                </form>
            </div>
        </div>
        <div class="row h-auto">
            <div class="col-sm-12 col-md-12 col-lg-12">
                <DataTable
                    v-model:filters="filters"
                    :value="filteredOptions"
                    paginator
                    :rows="10"
                    dataKey="id"
                    filterDisplay="row"
                    :loading="loading"
                    :globalFilterFields="[
                        'name',
                        'country.name',
                        'representative.name',
                        'status',
                    ]"
                >
                    <template #header>
                        <div class="flex justify-content-end">
                            <span class="p-input-icon-left">
                                <i class="pi pi-search" />
                                <InputText
                                    v-model="filters['global'].value"
                                    placeholder="Keyword Search"
                                />
                            </span>
                        </div>
                    </template>
                    <template #empty> No application selected. </template>
                    <template #loading>
                        Loading customers data. Please wait.
                    </template>
                    <Column
                        field="username"
                        header="User name"
                        sortable
                    ></Column>
                    <Column field="domain" header="Domain" sortable></Column>
                    <Column field="role" header="Role" sortable></Column>
                    <Column
                        field="forestClientId"
                        header="Forest Client ID"
                        sortable
                    ></Column>
                    <Column field="actions" header="Actions"></Column>
                </DataTable>
            </div>
        </div>
    </div>
</template>

<style scoped type="scss">
.application-dropdown {
    width: 304px;
}
</style>
