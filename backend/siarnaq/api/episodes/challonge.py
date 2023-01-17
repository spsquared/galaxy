# An API-esque module for our usage.
# Commands here are not very generic (like a good API),
# and are instead tailored to Battlecode's specific usage,
# to improve dev efficiency

import requests
from django.conf import settings

_headers = {
    "Accept": "application/json",
    "Authorization-Type": "v1",
    "Authorization": settings.CHALLONGE_API_KEY,
    "Content-Type": "application/vnd.api+json",
    # requests' default user agent causes Challonge's API to crash.
    "User-Agent": "",
}

AUTH_TYPE = "v1"
URL_BASE = "https://api.challonge.com/v2/"


def set_api_key(api_key):
    """Set the challonge.com api credentials to use."""
    _headers["Authorization"] = api_key


def create_tournament(
    tournament_url,
    tournament_name,
    is_private,
    style,
):
    from siarnaq.api.episodes.models import TournamentStyle

    # Challonge wants a specific string for tournament type.
    tournament_type = (
        "single elimination"
        if style == TournamentStyle.SINGLE_ELIMINATION
        else "double elimination"
    )

    url = f"{URL_BASE}tournaments.json"

    payload = {
        "data": {
            "type": "tournaments",
            "attributes": {
                "name": tournament_name,
                "tournament_type": tournament_type,
                "private": is_private,
                "url": tournament_url,
            },
        }
    }

    r = requests.post(url, headers=_headers, json=payload)
    r.raise_for_status()


def bulk_add_participants(tournament_url, participants):
    """
    Adds participants in bulk.
    Expects `participants` to be formatted in the format Challonge expects.
    Note especially that seeds must be 1-indexed.
    """
    url = f"{URL_BASE}tournaments/{tournament_url}/participants/bulk_add.json"

    payload = {
        "data": {
            "type": "Participant",
            "attributes": {
                "participants": participants,
            },
        }
    }

    r = requests.post(url, headers=_headers, json=payload)
    r.raise_for_status()


def start_tournament(tournament_url):
    url = f"{URL_BASE}tournaments/{tournament_url}/change_state.json"

    payload = {"data": {"type": "TournamentState", "attributes": {"state": "start"}}}

    r = requests.put(url, headers=_headers, json=payload)
    r.raise_for_status()


def get_tournament(tournament_url):
    url = f"{URL_BASE}tournaments/{tournament_url}.json"

    r = requests.get(url, headers=_headers)
    r.raise_for_status()
    return r.json()


def get_round_indexes(tournament_url):
    tournament_data = get_tournament(tournament_url)

    round_indexes = set()
    for item in tournament_data["included"]:
        match item:
            case {"type": "match", "attributes": attributes}:
                round_index = attributes["round"]
                round_indexes.add(round_index)

    return round_indexes


def update_match(tournament_url, match_id, match):
    url = f"{URL_BASE}tournaments/{tournament_url}/matches/{match_id}.json"

    payload = {
        "data": {
            "type": "Match",
            "attributes": {
                "match": match,
            },
        }
    }

    r = requests.put(url, headers=_headers, json=payload)
    r.raise_for_status()
