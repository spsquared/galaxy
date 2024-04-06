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
import type { UserProfilePublic } from './UserProfilePublic';
import {
    UserProfilePublicFromJSON,
    UserProfilePublicFromJSONTyped,
    UserProfilePublicToJSON,
} from './UserProfilePublic';

/**
 * 
 * @export
 * @interface UserPublic
 */
export interface UserPublic {
    /**
     * 
     * @type {number}
     * @memberof UserPublic
     */
    readonly id: number;
    /**
     * 
     * @type {UserProfilePublic}
     * @memberof UserPublic
     */
    profile?: UserProfilePublic;
    /**
     * Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
     * @type {string}
     * @memberof UserPublic
     */
    username: string;
    /**
     * Designates whether the user can log into this admin site.
     * @type {boolean}
     * @memberof UserPublic
     */
    readonly is_staff: boolean;
}

/**
 * Check if a given object implements the UserPublic interface.
 */
export function instanceOfUserPublic(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && "id" in value;
    isInstance = isInstance && "username" in value;
    isInstance = isInstance && "is_staff" in value;

    return isInstance;
}

export function UserPublicFromJSON(json: any): UserPublic {
    return UserPublicFromJSONTyped(json, false);
}

export function UserPublicFromJSONTyped(json: any, ignoreDiscriminator: boolean): UserPublic {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'profile': !exists(json, 'profile') ? undefined : UserProfilePublicFromJSON(json['profile']),
        'username': json['username'],
        'is_staff': json['is_staff'],
    };
}

export function UserPublicToJSON(value?: UserPublic | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'profile': UserProfilePublicToJSON(value.profile),
        'username': value.username,
    };
}
