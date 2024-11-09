<script setup lang="ts">
import Button from "@/components/common/Button.vue";
import SearchLocateIcon from "@carbon/icons-vue/es/search--locate/16";
import ForestClientCard from "@/components/grantaccess/ForestClientCard.vue";
import { AppActlApiService } from "@/services/ApiServiceFactory";
import { useMutation } from "@tanstack/vue-query";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";
import { type FamForestClientSchema } from "fam-app-acsctl-api";
import InputText from "primevue/inputtext";
import { ErrorMessage, Field } from "vee-validate";
import { computed, h, ref, watch } from "vue";
import NotificationMessage from "../common/NotificationMessage.vue";
import type { ForestClientNotificationType } from "@/types/NotificationTypes";

const props = withDefaults(
    defineProps<{
        role: FamRoleDto | null;
        appId: number;
        verifiedClients: FamForestClientSchema[]; // The verified forest client numbers in the form data
        fieldId?: string;
    }>(),
    {
        fieldId: "forestClients",
    }
);

const emit = defineEmits(["setVerifiedForestClients"]);

const setVerifiedForestClients = (clients: FamForestClientSchema[]) =>
    emit("setVerifiedForestClients", clients);

const isVerifying = ref<boolean>(false);
const forestClientNumbersInput = ref("");
const numbersToVerify = ref<string[]>([]);

const errorClientNumbers = ref<string[]>([]);
const notExistClientNumbers = ref<string[]>([]);
const duplicateClientNumbers = ref<string[]>([]);
const notActiveClientNumbers = ref<string[]>([]);

const notifications = computed<ForestClientNotificationType[]>(() => [
    {
        type: "Duplicate",
        severity: "warn",
        clientNumbers: duplicateClientNumbers.value,
    },
    {
        type: "Error",
        severity: "error",
        clientNumbers: errorClientNumbers.value,
    },
    {
        type: "NotExist",
        severity: "error",
        clientNumbers: notExistClientNumbers.value,
    },
    {
        type: "NotActive",
        severity: "error",
        clientNumbers: notActiveClientNumbers.value,
    },
]);

const clearNotifications = () => {
    errorClientNumbers.value = [];
    notExistClientNumbers.value = [];
    duplicateClientNumbers.value = [];
    notActiveClientNumbers.value = [];
};

const cleanupForestClientSection = () => {
    // remove the verified forest client numbers which already added to form data
    setVerifiedForestClients([]);

    clearNotifications();
};

// whenever user id or abstract role changed, cleanup the forest client section
watch(
    () => props.role,
    () => cleanupForestClientSection()
);

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
        const allClients = [
            ...verifiedClientsFromQuery,
            ...props.verifiedClients,
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
    let fcList = [...props.verifiedClients];
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
    verifyClients();
};

const generateNotificationMsg = (
    type: "NotExist" | "NotActive" | "Duplicate" | "Error"
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
            v-model="props.verifiedClients"
        >
            <div class="input-with-verify-button">
                <div>
                    <InputText
                        id="forestClientInput"
                        placeholder="Enter and verify the client number"
                        class="w-100 custom-height"
                        v-model="forestClientNumbersInput"
                        @keydown.enter.prevent="
                            forestClientNumbersInput.length &&
                                addClientNumbers()
                        "
                        :class="{
                            'is-invalid':
                                errorMessage || errorClientNumbers.length > 0,
                        }"
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
        v-if="verifiedClients.length > 0"
        class="fores-client-card-container custom-card px-0"
        :forestClientData="verifiedClients"
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
