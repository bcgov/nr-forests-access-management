import { BC_TIMEZONE, DATE_FORMAT, DATE_TIME_FORMAT, LUXON_DATE_FORMAT_YYYY_MM_DD } from "@/constants/DateFormats";
import { DateTime } from "luxon";

/**
 * Converts a UTC date-time string to the local user's time zone and formats it for display in a table.
 *
 * @param {string} utcDate - The UTC date-time string in ISO format (e.g., "2024-09-24T00:14:10.665421Z").
 * @returns {string} The date-time formatted according to the table format (e.g., "Jan 09, 2023 | 03:09 PM").
 */
export const utcToLocalDateTime = (utcDate: string): string =>
    DateTime.fromISO(utcDate).setZone("local").toFormat(DATE_TIME_FORMAT);

/**
 * Converts a UTC date-time string to the local user's time zone and formats it for display in a table.
 *
 * @param {string} utcDate - The UTC date-time string in ISO format (e.g., "2024-09-24T00:14:10.665421Z").
 * @returns {string} The date formatted according to the table format (e.g., "Jan 09, 2023").
 */
export const utcToLocalDate = (utcDate: string): string =>
    DateTime.fromISO(utcDate).setZone("local").toFormat(DATE_FORMAT);

/**
 * Converts the current date to the BC timezone (America/Vancouver).
 *
 * @returns {Date} A Date object representing the current date and time in the BC timezone.
 */
export const currentDateInBCTimezone = (): Date => {
    return DateTime.now().setZone(BC_TIMEZONE).toJSDate();
};

/**
 * Utility function to format a Date object to YYYY-MM-DD using Luxon
 *
 * @param {Date} date - The Date object to be formatted.
 * @returns {string} The date formatted as a string in the format YYYY-MM-DD.
 */
export const formatDateToYYYYMMDD = (date: Date): string => {
    return DateTime.fromJSDate(date).toFormat(LUXON_DATE_FORMAT_YYYY_MM_DD);
};
