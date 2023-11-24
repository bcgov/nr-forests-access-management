/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import { reactive, ref } from "vue"
import type { Severity } from "@/enum/SeverityEnum";

const defaultNotification = ({
    success: {msg: "", fullMsg: "", showFullMsg: false},
    warn: {msg: "", fullMsg: "", showFullMsg: false},
    error: {msg: "", fullMsg: "", showFullMsg: false},
});

export const notifications = ref(
    JSON.parse(JSON.stringify(defaultNotification))
);

export const pushNotification = (severity: Severity, message: string) => {
    notifications.value[severity].msg = message;
}

export const clearNotification = (severity: string) => {
    notifications.value[severity].msg = "";
    notifications.value[severity].fullMsg = "";
    notifications.value[severity].showFullMsg = false;
}

export const resetNotification = () => {
    notifications.value = JSON.parse(JSON.stringify(defaultNotification));
};

export const showFullNotificationMsg = (severity: Severity) => {
    notifications.value[severity].showFullMsg = false;
    pushNotification(severity, notifications.value[severity].fullMsg);
};

export const setNotificationMsg = (forestClientNumberList: string[], userId: any, severity: Severity) => {
    const isPlural = forestClientNumberList.length === 1 ? 'ID' : 'IDs'
    const msgByType = {
        success: `was successfully added with Client ${isPlural}:`,
        warn: `already exists with Client ${isPlural}:`,
        error: `was not added with Client ${isPlural}:`
    };

    const clientIdList = forestClientNumberList.slice(0 , 2);

    notifications.value[severity].fullMsg = `${userId} ${msgByType[severity]} ${forestClientNumberList.join(', ')}`;
    notifications.value[severity].showFullMsg = forestClientNumberList.length > 2

    const notificationMsg = `
        ${userId} ${msgByType[severity]} ${clientIdList.join(', ')}
        ${isPlural === 'IDs' && forestClientNumberList.length > 2 ?
        'and ' + (forestClientNumberList.length - 2) + ' more...'
        : ''}
    `;

    pushNotification(severity, notificationMsg);
};
