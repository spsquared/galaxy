/* tslint:disable */
/* eslint-disable */
/**
 * 
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

/**
 * 
 * @export
 * @enum {string}
 */
export enum ReleaseStatusEnum {
    NUMBER_0 = 0,
    NUMBER_1 = 1,
    NUMBER_2 = 2
}


export function ReleaseStatusEnumFromJSON(json: any): ReleaseStatusEnum {
    return ReleaseStatusEnumFromJSONTyped(json, false);
}

export function ReleaseStatusEnumFromJSONTyped(json: any, ignoreDiscriminator: boolean): ReleaseStatusEnum {
    return json as ReleaseStatusEnum;
}

export function ReleaseStatusEnumToJSON(value?: ReleaseStatusEnum | null): any {
    return value as any;
}

