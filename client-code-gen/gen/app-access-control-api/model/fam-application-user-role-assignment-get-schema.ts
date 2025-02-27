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
import { FamRoleWithClientSchema } from './fam-role-with-client-schema';
// May contain unused imports in some cases
// @ts-ignore
import { FamUserInfoSchema } from './fam-user-info-schema';

/**
 * 
 * @export
 * @interface FamApplicationUserRoleAssignmentGetSchema
 */
export interface FamApplicationUserRoleAssignmentGetSchema {
    /**
     * 
     * @type {number}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'user_role_xref_id': number;
    /**
     * 
     * @type {number}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'user_id': number;
    /**
     * 
     * @type {number}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'role_id': number;
    /**
     * 
     * @type {FamUserInfoSchema}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'user': FamUserInfoSchema;
    /**
     * 
     * @type {FamRoleWithClientSchema}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'role': FamRoleWithClientSchema;
    /**
     * 
     * @type {string}
     * @memberof FamApplicationUserRoleAssignmentGetSchema
     */
    'create_date': string;
}

