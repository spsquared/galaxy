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
import type { MatchParticipant } from './MatchParticipant';
import {
    MatchParticipantFromJSON,
    MatchParticipantFromJSONTyped,
    MatchParticipantToJSON,
} from './MatchParticipant';
import type { StatusBccEnum } from './StatusBccEnum';
import {
    StatusBccEnumFromJSON,
    StatusBccEnumFromJSONTyped,
    StatusBccEnumToJSON,
} from './StatusBccEnum';

/**
 * 
 * @export
 * @interface Match
 */
export interface Match {
    /**
     * 
     * @type {number}
     * @memberof Match
     */
    readonly id: number;
    /**
     * 
     * @type {StatusBccEnum}
     * @memberof Match
     */
    readonly status: StatusBccEnum;
    /**
     * 
     * @type {string}
     * @memberof Match
     */
    readonly episode: string;
    /**
     * 
     * @type {number}
     * @memberof Match
     */
    readonly tournament_round: number | null;
    /**
     * 
     * @type {Array<MatchParticipant>}
     * @memberof Match
     */
    participants: Array<MatchParticipant>;
    /**
     * 
     * @type {Array<string>}
     * @memberof Match
     */
    readonly maps: Array<string>;
    /**
     * 
     * @type {boolean}
     * @memberof Match
     */
    readonly alternate_order: boolean;
    /**
     * 
     * @type {Date}
     * @memberof Match
     */
    readonly created: Date;
    /**
     * 
     * @type {boolean}
     * @memberof Match
     */
    readonly is_ranked: boolean;
    /**
     * 
     * @type {string}
     * @memberof Match
     */
    readonly replay_url: string;
}

/**
 * Check if a given object implements the Match interface.
 */
export function instanceOfMatch(value: object): boolean {
    let isInstance = true;
    isInstance = isInstance && "id" in value;
    isInstance = isInstance && "status" in value;
    isInstance = isInstance && "episode" in value;
    isInstance = isInstance && "tournament_round" in value;
    isInstance = isInstance && "participants" in value;
    isInstance = isInstance && "maps" in value;
    isInstance = isInstance && "alternate_order" in value;
    isInstance = isInstance && "created" in value;
    isInstance = isInstance && "is_ranked" in value;
    isInstance = isInstance && "replay_url" in value;

    return isInstance;
}

export function MatchFromJSON(json: any): Match {
    return MatchFromJSONTyped(json, false);
}

export function MatchFromJSONTyped(json: any, ignoreDiscriminator: boolean): Match {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'status': StatusBccEnumFromJSON(json['status']),
        'episode': json['episode'],
        'tournament_round': json['tournament_round'],
        'participants': ((json['participants'] as Array<any>).map(MatchParticipantFromJSON)),
        'maps': json['maps'],
        'alternate_order': json['alternate_order'],
        'created': (new Date(json['created'])),
        'is_ranked': json['is_ranked'],
        'replay_url': json['replay_url'],
    };
}

export function MatchToJSON(value?: Match | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'participants': ((value.participants as Array<any>).map(MatchParticipantToJSON)),
    };
}

