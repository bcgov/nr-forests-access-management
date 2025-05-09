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
// @ts-ignore
import { FamForestClientSchema } from '../model';
// @ts-ignore
import { HTTPValidationError } from '../model';
/**
 * FAMForestClientsApi - axios parameter creator
 * @export
 */
export const FAMForestClientsApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * Forest Client(s) search (by defined query parameter(s)). param: \'client_number=[query_value]\'        Note! Current Forest Client API limits it to exact search for a whole 8-digits number. return: List of found FamForestClient. However, currently only 1 exact match returns.
         * @summary Search
         * @param {string} clientNumber 
         * @param {number} applicationId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        search: async (clientNumber: string, applicationId: number, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'clientNumber' is not null or undefined
            assertParamExists('search', 'clientNumber', clientNumber)
            // verify required parameter 'applicationId' is not null or undefined
            assertParamExists('search', 'applicationId', applicationId)
            const localVarPath = `/forest-clients/search`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            // authentication 6jfveou69mgford233or30hmta required
            // oauth required
            await setOAuthToObject(localVarHeaderParameter, "6jfveou69mgford233or30hmta", [], configuration)

            if (clientNumber !== undefined) {
                localVarQueryParameter['client_number'] = clientNumber;
            }

            if (applicationId !== undefined) {
                localVarQueryParameter['application_id'] = applicationId;
            }


    
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
 * FAMForestClientsApi - functional programming interface
 * @export
 */
export const FAMForestClientsApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = FAMForestClientsApiAxiosParamCreator(configuration)
    return {
        /**
         * Forest Client(s) search (by defined query parameter(s)). param: \'client_number=[query_value]\'        Note! Current Forest Client API limits it to exact search for a whole 8-digits number. return: List of found FamForestClient. However, currently only 1 exact match returns.
         * @summary Search
         * @param {string} clientNumber 
         * @param {number} applicationId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async search(clientNumber: string, applicationId: number, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<FamForestClientSchema>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.search(clientNumber, applicationId, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMForestClientsApi.search']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * FAMForestClientsApi - factory interface
 * @export
 */
export const FAMForestClientsApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = FAMForestClientsApiFp(configuration)
    return {
        /**
         * Forest Client(s) search (by defined query parameter(s)). param: \'client_number=[query_value]\'        Note! Current Forest Client API limits it to exact search for a whole 8-digits number. return: List of found FamForestClient. However, currently only 1 exact match returns.
         * @summary Search
         * @param {string} clientNumber 
         * @param {number} applicationId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        search(clientNumber: string, applicationId: number, options?: any): AxiosPromise<Array<FamForestClientSchema>> {
            return localVarFp.search(clientNumber, applicationId, options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * FAMForestClientsApi - interface
 * @export
 * @interface FAMForestClientsApi
 */
export interface FAMForestClientsApiInterface {
    /**
     * Forest Client(s) search (by defined query parameter(s)). param: \'client_number=[query_value]\'        Note! Current Forest Client API limits it to exact search for a whole 8-digits number. return: List of found FamForestClient. However, currently only 1 exact match returns.
     * @summary Search
     * @param {string} clientNumber 
     * @param {number} applicationId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMForestClientsApiInterface
     */
    search(clientNumber: string, applicationId: number, options?: RawAxiosRequestConfig): AxiosPromise<Array<FamForestClientSchema>>;

}

/**
 * FAMForestClientsApi - object-oriented interface
 * @export
 * @class FAMForestClientsApi
 * @extends {BaseAPI}
 */
export class FAMForestClientsApi extends BaseAPI implements FAMForestClientsApiInterface {
    /**
     * Forest Client(s) search (by defined query parameter(s)). param: \'client_number=[query_value]\'        Note! Current Forest Client API limits it to exact search for a whole 8-digits number. return: List of found FamForestClient. However, currently only 1 exact match returns.
     * @summary Search
     * @param {string} clientNumber 
     * @param {number} applicationId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMForestClientsApi
     */
    public search(clientNumber: string, applicationId: number, options?: RawAxiosRequestConfig) {
        return FAMForestClientsApiFp(this.configuration).search(clientNumber, applicationId, options).then((request) => request(this.axios, this.basePath));
    }
}

