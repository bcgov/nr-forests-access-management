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
import { UserType } from './user-type';

/**
 * 
 * @export
 * @interface FamUserRoleAssignmentCreate
 */
export interface FamUserRoleAssignmentCreate {
    /**
     * 
     * @type {string}
     * @memberof FamUserRoleAssignmentCreate
     */
    'user_name': string;
    /**
     * 
     * @type {string}
     * @memberof FamUserRoleAssignmentCreate
     */
    'user_guid': string;
    /**
     * 
     * @type {UserType}
     * @memberof FamUserRoleAssignmentCreate
     */
    'user_type_code': UserType;
    /**
     * 
     * @type {number}
     * @memberof FamUserRoleAssignmentCreate
     */
    'role_id': number;
    /**
     * 
     * @type {Array<string>}
     * @memberof FamUserRoleAssignmentCreate
     */
    'forest_client_numbers'?: Array<string> | null;
}



