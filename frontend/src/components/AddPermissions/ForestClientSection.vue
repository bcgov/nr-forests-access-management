<script setup lang="ts">
import Button from "@/components/UI/Button.vue";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import ForestClientCard from "@/components/AddPermissions/ForestClientCard.vue";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { useMutation } from "@tanstack/vue-query";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import { type FamForestClientSchema } from "fam-app-acsctl-api";
import InputText from "primevue/inputtext";
import { ErrorMessage, Field } from "vee-validate";
import { computed, h, inject, ref, watch, type Ref } from "vue";
import NotificationMessage from "../UI/NotificationMessage.vue";
import {
    Severity,
    type ForestClientNotificationType,
} from "@/types/NotificationTypes";
import { FOREST_CLIENT_INPUT_MAX_LENGTH } from "@/constants/constants";
import { APP_PERMISSION_FORM_KEY } from "@/constants/InjectionKeys";
import type { AppPermissionFormType } from "@/views/AddAppPermission/utils";

const formData = inject<Ref<AppPermissionFormType>>(APP_PERMISSION_FORM_KEY);

if (!formData) {
    throw new Error("formData is required but not provided");
}

const props = withDefaults(
    defineProps<{
        appId: number;
        fieldId?: string;
    }>(),
    {
        fieldId: "forestClients",
    }
);

const setVerifiedForestClients = (clients: FamForestClientSchema[]) => {
    formData.value.forestClients = clients;
};

const isVerifying = ref<boolean>(false);
const forestClientNumbersInput = ref("");
const numbersToVerify = ref<string[]>([]);

// Numbers that aren't exactly FOREST_CLIENT_INPUT_MAX_LENGTH long
const invalidClientNumbers = ref<string[]>([]);

// Numbers that encountered error while validating
const errorClientNumbers = ref<string[]>([]);

// Numbers that don't exist in Forest Client directory
const notExistClientNumbers = ref<string[]>([]);

// Numbers that have already been added
const duplicateClientNumbers = ref<string[]>([]);

// Numbers that are associated with an inactive forest client
const notActiveClientNumbers = ref<string[]>([]);

const notifications = computed<ForestClientNotificationType[]>(() => [
    {
        type: "Duplicate",
        severity: Severity.Warn,
        clientNumbers: duplicateClientNumbers.value,
    },
    {
        type: "Error",
        severity: Severity.Error,
        clientNumbers: errorClientNumbers.value,
    },
    {
        type: "NotExist",
        severity: Severity.Error,
        clientNumbers: notExistClientNumbers.value,
    },
    {
        type: "NotActive",
        severity: Severity.Error,
        clientNumbers: notActiveClientNumbers.value,
    },
    {
        type: "Invalid",
        severity: Severity.Error,
        clientNumbers: invalidClientNumbers.value,
    },
]);

const clearNotifications = () => {
    errorClientNumbers.value = [];
    notExistClientNumbers.value = [];
    duplicateClientNumbers.value = [];
    notActiveClientNumbers.value = [];
    invalidClientNumbers.value = [];
};

const clientSearchMutation = useMutation({
    mutationFn: (clientNumber: string) => {
        return AppActlApiService.forestClientsApi
            .search(clientNumber, props.appId)
            .then((res) => res.data);
    },
    onSuccess: (data, clientNumber) => {
        if (!data.length) {
            notExistClientNumbers.value.push(clientNumber);
        } else if (data[0].status?.status_code !== "A") {
            notActiveClientNumbers.value.push(clientNumber);
        }
    },
    onError: (_error, clientNumber) => {
        if (clientNumber) {
            errorClientNumbers.value.push(clientNumber);
        }
    },
});

const verifyClients = async () => {
    if (!isVerifying.value) {
        isVerifying.value = true;
        clearNotifications();
        duplicateClientNumbers.value = [];
        const verifyPromises = numbersToVerify.value.map((clientNumber) =>
            clientSearchMutation.mutateAsync(clientNumber)
        );

        const settledPromise = await Promise.allSettled(verifyPromises);

        isVerifying.value = false;
        forestClientNumbersInput.value = "";

        const verifiedClientsFromQuery: FamForestClientSchema[] = settledPromise
            .filter(
                (
                    promise
                ): promise is PromiseFulfilledResult<FamForestClientSchema[]> =>
                    promise.status === "fulfilled"
            )
            .map((data) =>
                data.value.length && data.value[0].status?.status_code === "A"
                    ? data.value[0]
                    : null
            )
            .filter((fc): fc is FamForestClientSchema => fc !== null);

        // Combine the two lists
        console.log(formData.value.role);
        const allClients = [
            ...verifiedClientsFromQuery,
            ...formData.value.forestClients,
        ];

        // Create a map to track occurrences
        const clientMap = new Map<string, FamForestClientSchema[]>();

        allClients.forEach((client) => {
            const key = client.forest_client_number;
            if (!clientMap.has(key)) {
                clientMap.set(key, [client]);
            } else {
                clientMap.get(key)!.push(client);
            }
        });

        // Extract unique clients
        const uniqueVerifiedClients = [
            ...Array.from(clientMap.values())
                .filter((clients) => clients.length)
                .map((clients) => clients[0]),
        ];

        // Extract duplicates
        const duppedClientNumbers = Array.from(clientMap.entries())
            .filter(([, clients]) => clients.length > 1)
            .map(([forest_client_number]) => forest_client_number);

        duplicateClientNumbers.value = duppedClientNumbers;

        setVerifiedForestClients(uniqueVerifiedClients);
    }
};

const removeForestClientFromList = (clientNumber: string) => {
    let fcList = [...formData.value.forestClients];
    // remove the verified forest client from card
    fcList = fcList.filter(
        (client) => client.forest_client_number !== clientNumber
    );

    // Emit the updated list
    setVerifiedForestClients(fcList);
};

const parseAndCleanNumbers = (input: string): string[] => {
    return Array.from(
        new Set(
            input
                .split(",")
                .map((num) => num.trim()) // Remove any surrounding spaces
                .filter((num) => num) // Remove empty strings if there are multiple commas
        )
    );
};

const addClientNumbers = () => {
    if (!forestClientNumbersInput.value) {
        return;
    }
    numbersToVerify.value = parseAndCleanNumbers(
        forestClientNumbersInput.value
    );

    const invalidNumbers = numbersToVerify.value.filter(
        (clientNumber) => clientNumber.length !== FOREST_CLIENT_INPUT_MAX_LENGTH
    );

    if (invalidNumbers.length) {
        invalidClientNumbers.value = invalidNumbers.map((clientNumber) =>
            clientNumber.length > FOREST_CLIENT_INPUT_MAX_LENGTH
                ? `${clientNumber.substring(
                      0,
                      FOREST_CLIENT_INPUT_MAX_LENGTH
                  )}...`
                : clientNumber
        );

        return;
    }

    verifyClients();
};

const generateNotificationMsg = (
    type: ForestClientNotificationType["type"]
) => {
    let clientNumbers: string[];
    let message: string;

    // Determine the appropriate client numbers and message for each type
    switch (type) {
        case "NotExist":
            clientNumbers = notExistClientNumbers.value;
            message =
                clientNumbers.length > 1 ? "do not exist" : "does not exist";
            break;
        case "NotActive":
            clientNumbers = notActiveClientNumbers.value;
            message =
                clientNumbers.length > 1 ? "are not active" : "is not active";
            break;
        case "Duplicate":
            clientNumbers = duplicateClientNumbers.value;
            message =
                clientNumbers.length > 1
                    ? "have already been added"
                    : "has already been added";
            break;
        case "Error":
            clientNumbers = errorClientNumbers.value;
            message = "encountered an error while being added";
            break;
        case "Invalid":
            clientNumbers = invalidClientNumbers.value;
            message = `
            ${clientNumbers.length > 1 ? "are" : "is"}
            not
            ${FOREST_CLIENT_INPUT_MAX_LENGTH} digits long
             `;
            break;
        default:
            clientNumbers = [];
            message = "encountered an error while being added";
            break;
    }

    // Map and format the client numbers
    const numberText = clientNumbers.map((number, index) => [
        h("b", number),
        index < clientNumbers.length - 1 ? ", " : "",
    ]);

    return h("p", {}, [
        "Client number",
        clientNumbers.length > 1 ? "s " : " ",
        ...numberText,
        ` ${message}`,
    ]);
};

const enforceNumberAndComma = (event: Event) => {
    const target = event.target as HTMLInputElement;
    let newValue = "";

    for (const char of target.value) {
        if ((char >= "0" && char <= "9") || char === "," || char === " ") {
            newValue += char;
        }
    }

    target.value = newValue;
    forestClientNumbersInput.value = newValue;
};
</script>

<template>
    <!-- Input section -->
    <div>
        <label for="forestClientInput">
            Organization's client number (8 digits)
        </label>
        <Field
            :name="props.fieldId"
            v-slot="{ errorMessage }"
            v-model="formData.forestClients"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="forestClientInput"
                        placeholder="Enter and verify the client number"
                        class="w-100 custom-height"
                        v-model="forestClientNumbersInput"
                        :maxlength="200"
                        @input="enforceNumberAndComma"
                        @keydown.enter.prevent="
                            forestClientNumbersInput.length &&
                                addClientNumbers()
                        "
                        :class="{
                            'is-invalid':
                                errorMessage || errorClientNumbers.length > 0,
                        }"
                        @blur="
                            forestClientNumbersInput.length &&
                                addClientNumbers()
                        "
                        :disabled="isVerifying"
                    />
                    <small
                        id="forestClientInput-help"
                        class="helper-text"
                        v-if="!errorMessage"
                        >Add one or more separated by commas</small
                    >
                    <ErrorMessage
                        class="invalid-feedback"
                        :name="props.fieldId"
                    />
                </div>
                <Button
                    outlined
                    aria-label="verify organizations"
                    name="verify organizations"
                    label="Verify"
                    @click="addClientNumbers"
                    :icon="SearchLocateIcon"
                    :is-loading="isVerifying"
                />
            </div>
        </Field>
    </div>

    <div v-for="notification in notifications">
        <NotificationMessage
            v-if="notification.clientNumbers.length"
            :key="notification.type"
            :message="generateNotificationMsg(notification.type)"
            :severity="notification.severity"
            class="forest-client-warn-notification"
            hide-severity-text
            :closable="false"
        />
    </div>

    <!-- Verified Card Section -->

    <ForestClientCard
        v-if="formData.forestClients.length > 0"
        class="fores-client-card-container custom-card px-0"
        :forestClientData="formData.forestClients"
        @remove-item="removeForestClientFromList"
    />
</template>

<style lang="scss">
@import "@/assets/styles/card.scss";
.fores-client-card-container {
    margin-top: 2rem;
}
.forest-client-warn-notification {
    .p-message {
        position: relative;
    }
}
</style>
