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
 * SmokeTestApi - axios parameter creator
 * @export
 */
export const SmokeTestApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * List of different applications that are administered by FAM
         * @summary Smoke Test
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        smokeTest: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/smoke_test`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;


    
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
 * SmokeTestApi - functional programming interface
 * @export
 */
export const SmokeTestApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = SmokeTestApiAxiosParamCreator(configuration)
    return {
        /**
         * List of different applications that are administered by FAM
         * @summary Smoke Test
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async smokeTest(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.smokeTest(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['SmokeTestApi.smokeTest']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * SmokeTestApi - factory interface
 * @export
 */
export const SmokeTestApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = SmokeTestApiFp(configuration)
    return {
        /**
         * List of different applications that are administered by FAM
         * @summary Smoke Test
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        smokeTest(options?: any): AxiosPromise<any> {
            return localVarFp.smokeTest(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * SmokeTestApi - interface
 * @export
 * @interface SmokeTestApi
 */
export interface SmokeTestApiInterface {
    /**
     * List of different applications that are administered by FAM
     * @summary Smoke Test
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SmokeTestApiInterface
     */
    smokeTest(options?: RawAxiosRequestConfig): AxiosPromise<any>;

}

/**
 * SmokeTestApi - object-oriented interface
 * @export
 * @class SmokeTestApi
 * @extends {BaseAPI}
 */
export class SmokeTestApi extends BaseAPI implements SmokeTestApiInterface {
    /**
     * List of different applications that are administered by FAM
     * @summary Smoke Test
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SmokeTestApi
     */
    public smokeTest(options?: RawAxiosRequestConfig) {
        return SmokeTestApiFp(this.configuration).smokeTest(options).then((request) => request(this.axios, this.basePath));
    }
}
