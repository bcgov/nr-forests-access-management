/*
    The notification state handles three types of notifications: success, warning and error.
    To assign a success message, for instance, import and use the pushSuccessNotification method.
    The same applies to warning and error messages. It is intended to be used in conjunction with
    the NotificationStack component.
*/

import { ref } from "vue"

const defaultNotification = {
    success: "",
    warn: "",
    error: "",
};

export const notifications = ref(
    JSON.parse(JSON.stringify(defaultNotification))
);

export const pushSuccessNotification = (message: string) => {
    notifications.value["success"] = message;
}

export const pushWarningNotification = (message: string) => {
    notifications.value["warn"] = message;
}

export const pushErrorNotification = (message: string) => {
    notifications.value["error"] = message;
}

export const clearNotification = (severity: string) => {
    notifications.value[severity] = '';
}

export const resetNotification = () => {
    notifications.value = JSON.parse(JSON.stringify(defaultNotification));
}