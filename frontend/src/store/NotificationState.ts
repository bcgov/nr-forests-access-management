/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import { ref } from 'vue';
import type { Severity } from '@/enum/SeverityEnum';

const defaultNotification = {
    success: { msg: '', fullMsg: '' },
    warn: { msg: '', fullMsg: '' },
    error: { msg: '', fullMsg: '' },
};

export const notifications = ref(
    JSON.parse(JSON.stringify(defaultNotification))
);

export const pushNotification = (severity: Severity, message: string) => {
    notifications.value[severity].msg = message;
};

export const clearNotification = (severity: string) => {
    notifications.value[severity].msg = '';
    notifications.value[severity].fullMsg = '';
};

export const resetNotification = () => {
    notifications.value = JSON.parse(JSON.stringify(defaultNotification));
};

export const showFullNotificationMsg = (severity: Severity) => {
    pushNotification(severity, notifications.value[severity].fullMsg);
};

export const setNotificationMsg = (
    forestClientNumberList: string[],
    userId: any,
    severity: Severity,
    role = ''
) => {
    const isPlural = forestClientNumberList.length === 1 ? 'ID' : 'IDs';
    const msgByType = {
        success:
            forestClientNumberList[0] === ''
                ? `was successfully added with the role ${role}`
                : `was successfully added with Client ${isPlural}:`,
        warn:
            forestClientNumberList[0] === ''
                ? `already exists with the role ${role}`
                : `already exists with Client ${isPlural}:`,
        error:
            forestClientNumberList[0] === ''
                ? `was not added with Client IDs: ${role}`
                : `was not added with Client ${isPlural}:`,
    };

    const clientIdList = forestClientNumberList.slice(0, 2);

    if (forestClientNumberList.length > 2)
        notifications.value[severity].fullMsg = `${userId} ${
            msgByType[severity]
        } ${forestClientNumberList.join(', ')}`;

    const notificationMsg = `
        ${userId} ${msgByType[severity]} ${clientIdList.join(', ')}
        ${
            isPlural === 'IDs' && forestClientNumberList.length > 2
                ? 'and ' + (forestClientNumberList.length - 2) + ' more...'
                : ''
        }
    `;

    pushNotification(severity, notificationMsg);
};
