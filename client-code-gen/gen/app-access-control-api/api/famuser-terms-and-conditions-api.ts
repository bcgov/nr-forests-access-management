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


import type { Configuration } from '../configuration';
import type { AxiosPromise, AxiosInstance, RawAxiosRequestConfig } from 'axios';
import globalAxios from 'axios';
// Some imports not used depending on template conditions
// @ts-ignore
import { DUMMY_BASE_URL, assertParamExists, setApiKeyToObject, setBasicAuthToObject, setBearerAuthToObject, setOAuthToObject, setSearchParams, serializeDataIfNeeded, toPathString, createRequestFunction } from '../common';
// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS, RequestArgs, BaseAPI, RequiredError, operationServerMap } from '../base';
/**
 * FAMUserTermsAndConditionsApi - axios parameter creator
 * @export
 */
export const FAMUserTermsAndConditionsApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * Create a record for terms and conditions acceptance.   If no version is provided, we store the 1st version of the terms and conditions.
         * @summary Create User Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createUserTermsAndConditions: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/user_terms_conditions`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'POST', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            // authentication 6jfveou69mgford233or30hmta required
            // oauth required
            await setOAuthToObject(localVarHeaderParameter, "6jfveou69mgford233or30hmta", [], configuration)


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * 
         * @summary Validate User Requires Accept Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        validateUserRequiresAcceptTermsAndConditions: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/user_terms_conditions/user:validate`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'POST', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            // authentication 6jfveou69mgford233or30hmta required
            // oauth required
            await setOAuthToObject(localVarHeaderParameter, "6jfveou69mgford233or30hmta", [], configuration)


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * FAMUserTermsAndConditionsApi - functional programming interface
 * @export
 */
export const FAMUserTermsAndConditionsApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = FAMUserTermsAndConditionsApiAxiosParamCreator(configuration)
    return {
        /**
         * Create a record for terms and conditions acceptance.   If no version is provided, we store the 1st version of the terms and conditions.
         * @summary Create User Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async createUserTermsAndConditions(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.createUserTermsAndConditions(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMUserTermsAndConditionsApi.createUserTermsAndConditions']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Validate User Requires Accept Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async validateUserRequiresAcceptTermsAndConditions(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<boolean>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.validateUserRequiresAcceptTermsAndConditions(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMUserTermsAndConditionsApi.validateUserRequiresAcceptTermsAndConditions']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * FAMUserTermsAndConditionsApi - factory interface
 * @export
 */
export const FAMUserTermsAndConditionsApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = FAMUserTermsAndConditionsApiFp(configuration)
    return {
        /**
         * Create a record for terms and conditions acceptance.   If no version is provided, we store the 1st version of the terms and conditions.
         * @summary Create User Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createUserTermsAndConditions(options?: any): AxiosPromise<any> {
            return localVarFp.createUserTermsAndConditions(options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Validate User Requires Accept Terms And Conditions
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        validateUserRequiresAcceptTermsAndConditions(options?: any): AxiosPromise<boolean> {
            return localVarFp.validateUserRequiresAcceptTermsAndConditions(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * FAMUserTermsAndConditionsApi - interface
 * @export
 * @interface FAMUserTermsAndConditionsApi
 */
export interface FAMUserTermsAndConditionsApiInterface {
    /**
     * Create a record for terms and conditions acceptance.   If no version is provided, we store the 1st version of the terms and conditions.
     * @summary Create User Terms And Conditions
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMUserTermsAndConditionsApiInterface
     */
    createUserTermsAndConditions(options?: RawAxiosRequestConfig): AxiosPromise<any>;

    /**
     * 
     * @summary Validate User Requires Accept Terms And Conditions
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMUserTermsAndConditionsApiInterface
     */
    validateUserRequiresAcceptTermsAndConditions(options?: RawAxiosRequestConfig): AxiosPromise<boolean>;

}

/**
 * FAMUserTermsAndConditionsApi - object-oriented interface
 * @export
 * @class FAMUserTermsAndConditionsApi
 * @extends {BaseAPI}
 */
export class FAMUserTermsAndConditionsApi extends BaseAPI implements FAMUserTermsAndConditionsApiInterface {
    /**
     * Create a record for terms and conditions acceptance.   If no version is provided, we store the 1st version of the terms and conditions.
     * @summary Create User Terms And Conditions
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMUserTermsAndConditionsApi
     */
    public createUserTermsAndConditions(options?: RawAxiosRequestConfig) {
        return FAMUserTermsAndConditionsApiFp(this.configuration).createUserTermsAndConditions(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Validate User Requires Accept Terms And Conditions
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMUserTermsAndConditionsApi
     */
    public validateUserRequiresAcceptTermsAndConditions(options?: RawAxiosRequestConfig) {
        return FAMUserTermsAndConditionsApiFp(this.configuration).validateUserRequiresAcceptTermsAndConditions(options).then((request) => request(this.axios, this.basePath));
    }
}
