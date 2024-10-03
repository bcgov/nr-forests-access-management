/**
 * Formats a user's full name and ID (userName) into a readable string.
 * If both first and last names are missing, it returns the ID only.
 * If either the first or last name is missing, it formats the remaining name with the ID.
 * If both names are present, it combines them with the ID.
 *
 * @param {string} userName - The unique identifier for the user.
 * @param {string} [firstName] - The optional first name of the user. Can be null.
 * @param {string} [lastName] - The optional last name of the user. Can be null.
 * @returns {string} - The formatted string in the format: "FirstName LastName (ID)",
 *                     or "LastName (ID)" if the first name is missing,
 *                     or "FirstName (ID)" if the last name is missing,
 *                     or just the "ID" if both names are missing.
 */
export const formatUserNameAndId = (
    userName: string,
    firstName?: string | null,
    lastName?: string | null,
): string => {
    if (!firstName && !lastName) {
        return userName;
    }

    if (!firstName) {
        return `${lastName} (${userName})`;
    }

    if (!lastName) {
        return `${firstName} (${userName})`;
    }

    return `${firstName} ${lastName} (${userName})`;
}
