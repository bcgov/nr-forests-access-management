/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import { ref } from 'vue';
import {
    ErrorDescription,
    ErrorCode,
    Severity,
    GrantPermissionType,
} from '@/enum/SeverityEnum';

interface Notification {
    severity: Severity;
    msg: string;
    fullMsg: string;
    showAll: boolean;
}

export const notifications = ref<Notification[]>([]);

export const resetNotification = () => (notifications.value = []);

export const setNotificationMsg = (
    severity: Severity,
    msg: string = '',
    fullMsg: string = ''
) => {
    const existingNotification = notifications.value.find(
        (notification) => notification.severity === severity
    );
    if (existingNotification) {
        existingNotification.msg = msg;
        existingNotification.fullMsg = fullMsg;
        existingNotification.showAll = fullMsg !== '';
    } else {
        notifications.value.push({
            severity: severity,
            msg: msg,
            fullMsg: fullMsg,
            showAll: fullMsg !== '',
        });
    }
};

export const showFullNotificationMsg = (severity: Severity) => {
    const notification = notifications.value.find(
        (notification) => notification.severity === severity
    );
    if (notification) {
        notification.msg = notification.fullMsg;
        notification.showAll = false;
    }
};

export interface CommonObjectType {
    [key: string]: any;
}

export const composeAndPushGrantPermissionNotification = (
    type: GrantPermissionType,
    userId: string,
    successList: string[],
    errorList: string[],
    errorCode: string,
    role: string = ''
) => {
    if (successList.length > 0) {
        setGrantPermissionNotificationMsg(
            type,
            Severity.Success,
            userId,
            successList,
            role
        );
    }

    if (errorList.length > 0) {
        setGrantPermissionNotificationMsg(
            type,
            Severity.Error,
            userId,
            errorList,
            role,
            errorCode
        );
    }
};

export const setGrantPermissionNotificationMsg = (
    type: GrantPermissionType,
    severity: Severity,
    userId: string,
    forestClientNumberList: string[],
    role: string = '',
    errorCode: string = ErrorCode.Default
) => {
    const msgByType: CommonObjectType = formataAndGetMsgByGrantType(
        type,
        userId,
        role,
        forestClientNumberList
    );

    const notificationMsg =
        severity == Severity.Success
            ? msgByType[severity]
            : msgByType[severity][errorCode];

    // when there are more than 2 forest client numbers, set full message to include all forest client numbers
    // replace the message after ':' to be the whole forest client number list
    const notificationFullMsg =
        forestClientNumberList.length > 2
            ? `${notificationMsg.split(':')[0]}: ${forestClientNumberList.join(
                  ', '
              )}`
            : '';

    setNotificationMsg(severity, notificationMsg, notificationFullMsg);
};

const formataAndGetMsgByGrantType = (
    grantType: string,
    userId: string,
    role: string,
    forestClientNumberList: string[] = []
) => {
    const isPlural = forestClientNumberList.length === 1 ? 'ID' : 'IDs';
    const firstTwoForestClientList = forestClientNumberList.slice(0, 2);
    // for example: forestClientMsg = "00001011, 00001012",
    // or forestClientMsg = "00001011, 00001012 and more" when there are more than 2 forest client numbers
    const forestClientMsg = `${firstTwoForestClientList.join(', ')} ${
        forestClientNumberList.length > 2
            ? 'and ' + (forestClientNumberList.length - 2) + ' more...'
            : ''
    }`;

    const msgForGrantConcreteRole = `the role ${role}`;
    const msgForGrantAbstractRole = `Client ${isPlural}: ${forestClientMsg}`;
    const msgByRoleType =
        forestClientNumberList.length == 1 && forestClientNumberList[0] == ''
            ? msgForGrantConcreteRole
            : msgForGrantAbstractRole;

    const msgByType: CommonObjectType = {
        [GrantPermissionType.Regular]: {
            [Severity.Success]: `${userId} was successfully added with ${msgByRoleType}`,
            [Severity.Error]: {
                [ErrorCode.Conflict]: `${userId} already exists with ${msgByRoleType}`,
                [ErrorCode.SelfGrantProhibited]: `${ErrorDescription.SelfGrantProhibited} ${userId} was not added with ${msgByRoleType}`,
                [ErrorCode.Default]: `${ErrorDescription.Default} ${userId} was not added with ${msgByRoleType}`,
            },
        },
        [GrantPermissionType.DelegatedAdmin]: {
            [Severity.Success]: `${userId} was successfully granted privilege to manage ${msgByRoleType}`,
            [Severity.Error]: {
                [ErrorCode.Conflict]: `${userId} already has the privilege to manage ${msgByRoleType}`,
                [ErrorCode.SelfGrantProhibited]: `${ErrorDescription.SelfGrantProhibited} ${userId} was not granted privilege to manage ${msgByRoleType}`,
                [ErrorCode.Default]: `${ErrorDescription.Default} ${userId} was not granted privilege to manage ${msgByRoleType}`,
            },
        },
    };

    return msgByType[grantType];
};
