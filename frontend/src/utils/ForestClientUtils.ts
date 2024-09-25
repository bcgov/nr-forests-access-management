/**
 * Converts a fully uppercase string into human-readable format.
 * Capitalizes the first letter of each word and converts the rest to lowercase,
 * with special exceptions for words like 'of', 'and', etc.
 *
 * @param {string} str - The input string in uppercase.
 * @returns {string} - The human-readable formatted string.
 */
const toHumanReadableFormat = (str?: string | null): string => {
    if (!str) return '';

    // List of words to always keep in lowercase unless they are the first word
    const exceptions = ['of', 'and', 'the', 'in', 'on', 'at', 'for', 'with', 'by'];

    return str
        .toLowerCase()
        .split(' ')
        .map((word: string, index: number) => {
            // Capitalize the first word or any word that is not in the exceptions list
            if (index === 0 || !exceptions.includes(word)) {
                return word.charAt(0).toUpperCase() + word.slice(1);
            }
            // Keep the word in lowercase if it is in the exceptions list
            return word;
        })
        .join(' ');
};

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
        return toHumanReadableFormat(clientName);
    }

    if (clientId && !clientName) {
        return clientId;
    }

    if (!clientId && !clientName) {
        return 'Forest Client Data Not Available';
    }

    return `${toHumanReadableFormat(clientName)} (${clientId})`;
};
