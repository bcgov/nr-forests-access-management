/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import { ref } from 'vue';
import { ErrorDescription, type Severity } from '@/enum/SeverityEnum';

const defaultNotification = {
    success: { msg: '', fullMsg: '' },
    warn: { msg: '', fullMsg: '' },
    error: { msg: '', fullMsg: '' },
};

export const notifications = ref(
    JSON.parse(JSON.stringify(defaultNotification))
);

export const clearNotification = (severity: string) => {
    notifications.value[severity].msg = '';
    notifications.value[severity].fullMsg = '';
};

export const resetNotification = () => {
    notifications.value = JSON.parse(JSON.stringify(defaultNotification));
};

export const setNotificationMsg = (
    severity: Severity,
    msg: string = '',
    fullMsg: string = ''
) => {
    notifications.value[severity].msg = msg;
    notifications.value[severity].fullMsg = fullMsg;
};

export const showFullNotificationMsg = (severity: Severity) => {
    notifications.value[severity].msg = notifications.value[severity].fullMsg;
};

export interface CommonObjectType {
    [key: string]: any;
}

export const setGrantAccessNotificationMsg = (
    forestClientNumberList: string[],
    userId: string,
    severity: Severity,
    role = '',
    code: string = 'default'
) => {
    let notificationFullMsg = '';

    const isPlural = forestClientNumberList.length === 1 ? 'ID' : 'IDs';
    const msgByType: CommonObjectType = {
        success: {
            default:
                forestClientNumberList[0] === ''
                    ? `${userId} was successfully added with the role ${role}`
                    : `${userId} was successfully added with Client ${isPlural}:`,
        },
        error: {
            conflict:
                forestClientNumberList[0] === ''
                    ? `${userId} already exists with the role ${role}`
                    : `${userId} already exists with Client ${isPlural}:`,
            selfGrantProhibited:
                forestClientNumberList[0] === ''
                    ? `${ErrorDescription.SelfGrantProhibited} ${userId} was not added with the role: ${role}`
                    : `${ErrorDescription.SelfGrantProhibited} ${userId} was not added with Client ${isPlural}:`,
            default:
                forestClientNumberList[0] === ''
                    ? `${ErrorDescription.Default} ${userId} was not added with the role: ${role}`
                    : `${ErrorDescription.Default} ${userId} was not added with Client ${isPlural}:`,
        },
    };

    const clientIdList = forestClientNumberList.slice(0, 2);
    if (forestClientNumberList.length > 2) {
        notificationFullMsg = `${
            msgByType[severity][code]
        } ${forestClientNumberList.join(', ')}`;
    }

    const notificationMsg = `
        ${msgByType[severity][code]} ${clientIdList.join(', ')}
        ${
            isPlural === 'IDs' && forestClientNumberList.length > 2
                ? 'and ' + (forestClientNumberList.length - 2) + ' more...'
                : ''
        }
    `;

    setNotificationMsg(severity, notificationMsg, notificationFullMsg);
};
