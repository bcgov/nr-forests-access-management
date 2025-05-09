import { DateTime } from "luxon";
import { DATE_FORMAT, DATE_TIME_FORMAT } from "@/constants/DateFormats";

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
