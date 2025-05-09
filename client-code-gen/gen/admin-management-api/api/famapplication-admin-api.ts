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


import type { Configuration } from '../configuration';
import type { AxiosPromise, AxiosInstance, RawAxiosRequestConfig } from 'axios';
import globalAxios from 'axios';
// Some imports not used depending on template conditions
// @ts-ignore
import { DUMMY_BASE_URL, assertParamExists, setApiKeyToObject, setBasicAuthToObject, setBearerAuthToObject, setOAuthToObject, setSearchParams, serializeDataIfNeeded, toPathString, createRequestFunction } from '../common';
// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS, RequestArgs, BaseAPI, RequiredError, operationServerMap } from '../base';
// @ts-ignore
import { FamAppAdminCreateRequest } from '../model';
// @ts-ignore
import { FamAppAdminGetResponse } from '../model';
// @ts-ignore
import { HTTPValidationError } from '../model';
/**
 * FAMApplicationAdminApi - axios parameter creator
 * @export
 */
export const FAMApplicationAdminApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * 
         * @summary Create Application Admin
         * @param {FamAppAdminCreateRequest} famAppAdminCreateRequest 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createApplicationAdmin: async (famAppAdminCreateRequest: FamAppAdminCreateRequest, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'famAppAdminCreateRequest' is not null or undefined
            assertParamExists('createApplicationAdmin', 'famAppAdminCreateRequest', famAppAdminCreateRequest)
            const localVarPath = `/application-admins`;
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


    
            localVarHeaderParameter['Content-Type'] = 'application/json';

            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};
            localVarRequestOptions.data = serializeDataIfNeeded(famAppAdminCreateRequest, localVarRequestOptions, configuration)

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * 
         * @summary Delete Application Admin
         * @param {number} applicationAdminId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteApplicationAdmin: async (applicationAdminId: number, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'applicationAdminId' is not null or undefined
            assertParamExists('deleteApplicationAdmin', 'applicationAdminId', applicationAdminId)
            const localVarPath = `/application-admins/{application_admin_id}`
                .replace(`{${"application_admin_id"}}`, encodeURIComponent(String(applicationAdminId)));
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'DELETE', ...baseOptions, ...options};
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
         * @summary Export application admins information
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        exportApplicationAdmins: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/application-admins/export`;
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
         * @summary Get Application Admins
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getApplicationAdmins: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/application-admins`;
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
 * FAMApplicationAdminApi - functional programming interface
 * @export
 */
export const FAMApplicationAdminApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = FAMApplicationAdminApiAxiosParamCreator(configuration)
    return {
        /**
         * 
         * @summary Create Application Admin
         * @param {FamAppAdminCreateRequest} famAppAdminCreateRequest 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async createApplicationAdmin(famAppAdminCreateRequest: FamAppAdminCreateRequest, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<FamAppAdminGetResponse>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.createApplicationAdmin(famAppAdminCreateRequest, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMApplicationAdminApi.createApplicationAdmin']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Delete Application Admin
         * @param {number} applicationAdminId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async deleteApplicationAdmin(applicationAdminId: number, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<void>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.deleteApplicationAdmin(applicationAdminId, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMApplicationAdminApi.deleteApplicationAdmin']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Export application admins information
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async exportApplicationAdmins(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.exportApplicationAdmins(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMApplicationAdminApi.exportApplicationAdmins']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Get Application Admins
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async getApplicationAdmins(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<FamAppAdminGetResponse>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.getApplicationAdmins(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['FAMApplicationAdminApi.getApplicationAdmins']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * FAMApplicationAdminApi - factory interface
 * @export
 */
export const FAMApplicationAdminApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = FAMApplicationAdminApiFp(configuration)
    return {
        /**
         * 
         * @summary Create Application Admin
         * @param {FamAppAdminCreateRequest} famAppAdminCreateRequest 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createApplicationAdmin(famAppAdminCreateRequest: FamAppAdminCreateRequest, options?: any): AxiosPromise<FamAppAdminGetResponse> {
            return localVarFp.createApplicationAdmin(famAppAdminCreateRequest, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Delete Application Admin
         * @param {number} applicationAdminId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteApplicationAdmin(applicationAdminId: number, options?: any): AxiosPromise<void> {
            return localVarFp.deleteApplicationAdmin(applicationAdminId, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Export application admins information
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        exportApplicationAdmins(options?: any): AxiosPromise<any> {
            return localVarFp.exportApplicationAdmins(options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Get Application Admins
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getApplicationAdmins(options?: any): AxiosPromise<Array<FamAppAdminGetResponse>> {
            return localVarFp.getApplicationAdmins(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * FAMApplicationAdminApi - interface
 * @export
 * @interface FAMApplicationAdminApi
 */
export interface FAMApplicationAdminApiInterface {
    /**
     * 
     * @summary Create Application Admin
     * @param {FamAppAdminCreateRequest} famAppAdminCreateRequest 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApiInterface
     */
    createApplicationAdmin(famAppAdminCreateRequest: FamAppAdminCreateRequest, options?: RawAxiosRequestConfig): AxiosPromise<FamAppAdminGetResponse>;

    /**
     * 
     * @summary Delete Application Admin
     * @param {number} applicationAdminId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApiInterface
     */
    deleteApplicationAdmin(applicationAdminId: number, options?: RawAxiosRequestConfig): AxiosPromise<void>;

    /**
     * 
     * @summary Export application admins information
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApiInterface
     */
    exportApplicationAdmins(options?: RawAxiosRequestConfig): AxiosPromise<any>;

    /**
     * 
     * @summary Get Application Admins
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApiInterface
     */
    getApplicationAdmins(options?: RawAxiosRequestConfig): AxiosPromise<Array<FamAppAdminGetResponse>>;

}

/**
 * FAMApplicationAdminApi - object-oriented interface
 * @export
 * @class FAMApplicationAdminApi
 * @extends {BaseAPI}
 */
export class FAMApplicationAdminApi extends BaseAPI implements FAMApplicationAdminApiInterface {
    /**
     * 
     * @summary Create Application Admin
     * @param {FamAppAdminCreateRequest} famAppAdminCreateRequest 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApi
     */
    public createApplicationAdmin(famAppAdminCreateRequest: FamAppAdminCreateRequest, options?: RawAxiosRequestConfig) {
        return FAMApplicationAdminApiFp(this.configuration).createApplicationAdmin(famAppAdminCreateRequest, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Delete Application Admin
     * @param {number} applicationAdminId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApi
     */
    public deleteApplicationAdmin(applicationAdminId: number, options?: RawAxiosRequestConfig) {
        return FAMApplicationAdminApiFp(this.configuration).deleteApplicationAdmin(applicationAdminId, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Export application admins information
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApi
     */
    public exportApplicationAdmins(options?: RawAxiosRequestConfig) {
        return FAMApplicationAdminApiFp(this.configuration).exportApplicationAdmins(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Get Application Admins
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof FAMApplicationAdminApi
     */
    public getApplicationAdmins(options?: RawAxiosRequestConfig) {
        return FAMApplicationAdminApiFp(this.configuration).getApplicationAdmins(options).then((request) => request(this.axios, this.basePath));
    }
}

