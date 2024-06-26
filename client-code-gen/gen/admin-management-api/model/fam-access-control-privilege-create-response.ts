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


// May contain unused imports in some cases
// @ts-ignore
import { FamAccessControlPrivilegeGetResponse } from './fam-access-control-privilege-get-response';

/**
 * 
 * @export
 * @interface FamAccessControlPrivilegeCreateResponse
 */
export interface FamAccessControlPrivilegeCreateResponse {
    /**
     * 
     * @type {number}
     * @memberof FamAccessControlPrivilegeCreateResponse
     */
    'status_code': number;
    /**
     * 
     * @type {FamAccessControlPrivilegeGetResponse}
     * @memberof FamAccessControlPrivilegeCreateResponse
     */
    'detail': FamAccessControlPrivilegeGetResponse;
    /**
     * 
     * @type {string}
     * @memberof FamAccessControlPrivilegeCreateResponse
     */
    'error_message'?: string | null;
}

