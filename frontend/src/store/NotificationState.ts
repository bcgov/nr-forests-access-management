/*
    The notification state handles three types of notifications: success, warning and error.
    It is structured this way so it doesn't stack multiple messages with the same severity (by design).
    It is intended to be used in conjunction with the NotificationStack component.
*/
import { reactive, ref } from "vue"
import type { Severity } from "@/enum/SeverityEnum";

const defaultNotification = {
    success: "",
    warn: "",
    error: "",
};

export const seeAll = reactive({
    seeAllMsg: {
        success: {msg: "", isVisible: false},
        warn: {msg: "", isVisible: false},
        error: {msg: "", isVisible: false},
    },
    showAll(severity: Severity) {
        this.seeAllMsg[severity].isVisible = false;
        pushNotification(severity, this.seeAllMsg[severity].msg);
    }
});

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
};

export const setNotificationMsg = (forestClientNumberList: string[], userId: any, severity: Severity) => {
    seeAll.seeAllMsg[severity].isVisible = true;
    const isPlural = forestClientNumberList.length === 1 ? 'ID' : 'IDs'
    const msgByType = {
        success: `was successfully added with Client ${isPlural}:`,
        warn: `already exists with Client ${isPlural}:`,
        error: `was not added with Client ${isPlural}:`
    };

    const clientIdList = forestClientNumberList.slice(0 , 3);

    seeAll.seeAllMsg[severity].msg = `${userId} ${msgByType[severity]} ${forestClientNumberList.join(', ')}`;

    seeAll.seeAllMsg[severity].isVisible = forestClientNumberList.length > 3

    const notificationMsg = `
        ${userId} ${msgByType[severity]} ${clientIdList.join(', ')}
        ${isPlural === 'IDs' && forestClientNumberList.length > 3 ?
        'and ' + (forestClientNumberList.length - 3) + ' more...'
        : ''}
    `;
    pushNotification(severity, notificationMsg);
};
