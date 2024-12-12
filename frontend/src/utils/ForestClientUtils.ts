import { PLACE_HOLDER } from "../constants/constants";

/**
 * Formats the forest client display name by combining the client name and client ID.
 * If only the client name is provided, it returns the client name.
 * If only the client ID is provided, it returns the client ID.
 * If neither is provided, it returns a default message.
 *
 * @param {string} [clientId] - The optional unique identifier for the forest client.
 * @param {string} [clientName] - The optional name of the forest client.
 * @returns {string} A formatted string combining client name and ID, or the available value, or
 * a default message if both are unavailable.
 */
export const formatForestClientDisplayName = (
    clientId?: string | null,
    clientName?: string | null
): string => {
    if (!clientId && clientName) {
        return clientName;
    }

    if (clientId && !clientName) {
        return clientId;
    }

    if (!clientId && !clientName) {
        return PLACE_HOLDER;
    }

    return `${clientName} (${clientId})`;
};
