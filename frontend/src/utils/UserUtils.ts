import { PLACE_HOLDER } from "@/constants/constants";

/**
 * Formats a user's full name and ID (userName) into a readable string.
 * If both first and last names are missing, it returns the ID only if present.
 * If either the first or last name is missing, it formats the remaining name with the ID if available.
 * If all parameters are missing, it returns "Unknown User".
 *
 * @param {string | null} [userName] - The optional unique identifier for the user. Can be null.
 * @param {string | null} [firstName] - The optional first name of the user. Can be null.
 * @param {string | null} [lastName] - The optional last name of the user. Can be null.
 * @returns {string} - The formatted string in the format: "FirstName LastName (ID)",
 *                     or "LastName (ID)" if the first name is missing,
 *                     or "FirstName (ID)" if the last name is missing,
 *                     or just the "ID" if both names are missing but the ID is available,
 *                     or "Unknown User" if all parameters are missing.
 */
export const formatUserNameAndId = (
    userName?: string | null,
    firstName?: string | null,
    lastName?: string | null
): string => {
    if (!firstName && !lastName) {
        return userName ?? "";
    }

    if (!firstName) {
        return lastName + (userName ? ` (${userName})` : "");
    }

    if (!lastName) {
        return firstName + (userName ? ` (${userName})` : "");
    }

    return `${firstName} ${lastName}${userName ? ` (${userName})` : ""}`;
};

/**
 * Formats a user's full name into a readable string.
 * If both first and last names are missing, it returns an empty string.
 * If either the first or last name is missing, it formats the remaining name.
 * If both names are present, it combines them.
 *
 * @param {string} [firstName] - The optional first name of the user. Can be null.
 * @param {string} [lastName] - The optional last name of the user. Can be null.
 * @returns {string} - The formatted string in the format: "FirstName LastName",
 *                     or just "LastName" if the first name is missing,
 *                     or "FirstName" if the last name is missing,
 *                     or a PLACE_HOLDER string if both names are missing.
 */
export const formatFullName = (
    firstName?: string | null,
    lastName?: string | null
): string => {
    if (!firstName && !lastName) {
        return PLACE_HOLDER;
    }

    if (!firstName) {
        return lastName!;
    }

    if (!lastName) {
        return firstName!;
    }

    return `${firstName} ${lastName}`;
};
