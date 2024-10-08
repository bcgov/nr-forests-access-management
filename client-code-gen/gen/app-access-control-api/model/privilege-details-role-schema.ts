/* tslint:disable */
/* eslint-disable */
/**
 * Forest Access Management - FAM - API
 *  Forest Access Management API used by the Forest Access Management application to Define who has access to what apps, and what roles they will operate under  once access is granted. 
 *
 * The version of the OpenAPI document: 0.0.1
 * Contact: SIBIFSAF@victoria1.gov.bc.ca
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


// May contain unused imports in some cases
// @ts-ignore
import { PrivilegeDetailsScopeSchema } from './privilege-details-scope-schema';

/**
 * 
 * @export
 * @interface PrivilegeDetailsRoleSchema
 */
export interface PrivilegeDetailsRoleSchema {
    /**
     * 
     * @type {string}
     * @memberof PrivilegeDetailsRoleSchema
     */
    'role': string;
    /**
     * 
     * @type {Array<PrivilegeDetailsScopeSchema>}
     * @memberof PrivilegeDetailsRoleSchema
     */
    'scopes'?: Array<PrivilegeDetailsScopeSchema> | null;
}

