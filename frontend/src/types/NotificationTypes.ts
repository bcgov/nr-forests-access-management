import type { SeverityType } from "../enum/SeverityEnum";

export type ForestClientNotificationType = {
    type: "Duplicate" | "Error" | "NotExist" | "NotActive";
    severity: SeverityType;
    clientNumbers: string[];
};
