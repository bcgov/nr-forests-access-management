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
 * FAM data model does not explicitly have these role group of admins. However, business rules do differentiate purpose of admins as:     (FAM_ADMIN, [APP]_ADMIN, DELEGATED_ADMIN) - Referencing to FAM confluence for design:   https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Delegated+Access+Administration+Design (Auth Function)
 * @export
 * @enum {string}
 */

export const AdminRoleAuthGroup = {
    FamAdmin: 'FAM_ADMIN',
    AppAdmin: 'APP_ADMIN',
    DelegatedAdmin: 'DELEGATED_ADMIN'
} as const;

export type AdminRoleAuthGroup = typeof AdminRoleAuthGroup[keyof typeof AdminRoleAuthGroup];



