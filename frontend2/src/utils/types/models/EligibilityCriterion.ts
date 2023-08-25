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

import { exists, mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface EligibilityCriterion
 */
export interface EligibilityCriterion {
    /**
     * 
     * @type {number}
     * @memberof EligibilityCriterion
     */
    readonly id: number;
    /**
     * 
     * @type {string}
     * @memberof EligibilityCriterion
     */
    readonly title: string;
    /**
     * 
     * @type {string}
     * @memberof EligibilityCriterion
     */
    readonly description: string;
    /**
     * 
     * @type {string}
     * @memberof EligibilityCriterion
     */
    readonly icon: string;
}

/**
 * Check if a given object implements the EligibilityCriterion interface.
 */
export function instanceOfEligibilityCriterion(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && "id" in value;
    isInstance = isInstance && "title" in value;
    isInstance = isInstance && "description" in value;
    isInstance = isInstance && "icon" in value;

    return isInstance;
}

export function EligibilityCriterionFromJSON(json: any): EligibilityCriterion {
    return EligibilityCriterionFromJSONTyped(json, false);
}

export function EligibilityCriterionFromJSONTyped(json: any, ignoreDiscriminator: boolean): EligibilityCriterion {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'title': json['title'],
        'description': json['description'],
        'icon': json['icon'],
    };
}

export function EligibilityCriterionToJSON(value?: EligibilityCriterion | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
    };
}

