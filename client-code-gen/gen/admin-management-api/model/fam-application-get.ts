/* tslint:disable */
/* eslint-disable */
/**
 * Forest Access Management - FAM - Admin Management API
 *  Forest Access Management Admin Management API used by the Forest Access Management application to define admin access to forest applications. 
 *
 * The version of the OpenAPI document: 0.0.1
 * Contact: SIBIFSAF@Victoria1.gov.bc.ca
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


// May contain unused imports in some cases
// @ts-ignore
import { AppEnv } from './app-env';

/**
 * 
 * @export
 * @interface FamApplicationGet
 */
export interface FamApplicationGet {
    /**
     * 
     * @type {string}
     * @memberof FamApplicationGet
     */
    'application_name': string;
    /**
     * 
     * @type {string}
     * @memberof FamApplicationGet
     */
    'application_description': string;
    /**
     * 
     * @type {AppEnv}
     * @memberof FamApplicationGet
     */
    'app_environment'?: AppEnv | null;
    /**
     * 
     * @type {number}
     * @memberof FamApplicationGet
     */
    'application_id': number;
}


