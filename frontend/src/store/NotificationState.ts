/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import type { Severity } from "@/enum/SeverityEnum";
import { ref } from "vue"

const defaultNotification = {
    success: "",
    warn: "",
    error: "",
};

export const notifications = ref(
    JSON.parse(JSON.stringify(defaultNotification))
);

export const pushNotification = (severity: Severity, message: string) => {
    notifications.value[severity] = message;
}

export const clearNotification = (severity: string) => {
    notifications.value[severity] = '';
}

export const resetNotification = () => {
    notifications.value = JSON.parse(JSON.stringify(defaultNotification));
}
