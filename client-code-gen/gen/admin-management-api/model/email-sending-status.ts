/* tslint:disable */
/* eslint-disable */
/**
 * Forest Access Management - FAM - Admin Management API
 *  Forest Access Management Admin Management API used by the Forest Access Management application to define admin access to forest applications. 
 *
 * The version of the OpenAPI document: 0.0.1
 * Contact: SIBIFSAF@victoria1.gov.bc.ca
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */



/**
 * 
 * @export
 * @enum {string}
 */

export const EmailSendingStatus = {
    NotRequired: 'NOT_REQUIRED',
    SentToEmailServiceSuccess: 'SENT_TO_EMAIL_SERVICE_SUCCESS',
    SentToEmailServiceFailure: 'SENT_TO_EMAIL_SERVICE_FAILURE'
} as const;

export type EmailSendingStatus = typeof EmailSendingStatus[keyof typeof EmailSendingStatus];


