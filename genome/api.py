"""Retrieval of geopolitical events from the GENOME API."""

import requests
import pandas as pd

from genome.config import BASE_URL, API_KEY


def get_events_list(api_response_data):
    """Robustly extract the list of events from the API response.

    The API may return the events either as a bare list or nested inside a dict
    under one of several possible keys. This helper normalises both shapes.
    """
    if isinstance(api_response_data, list):
        return api_response_data

    if isinstance(api_response_data, dict):
        common_keys = ["items", "data", "results", "events"]
        for key in common_keys:
            if key in api_response_data and isinstance(api_response_data[key], list):
                return api_response_data[key]
        # Fall back to the first list-valued entry we find.
        for value in api_response_data.values():
            if isinstance(value, list):
                return value
        return [api_response_data]

    return []


def scrape_api_data(actor_countries, recipient, date_from, date_to):
    """Fetch events for one or more actor countries and return a DataFrame.

    Parameters
    ----------
    actor_countries : list[str]
        Actor countries to query. An empty list queries all actors.
    recipient : str
        Optional recipient country filter (empty string = any).
    date_from, date_to : str
        Optional ISO dates (YYYY-MM-DD) to bound the query.
    """
    headers = {"x-api-key": API_KEY, "Accept": "application/json"}

    print("=" * 58)
    all_events_data = []

    # Query each actor separately so we can tag every event with the actor it
    # was retrieved under (used later as `_queried_actor`).
    actors_to_query = actor_countries if actor_countries else [None]

    for actor in actors_to_query:
        params = {}
        if actor:
            params["actor_country"] = actor
            print(f"Fetching events for Actor: {actor}")
        else:
            print("Fetching events for all Actors...")

        if recipient:
            params["recipient"] = recipient
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        try:
            response = requests.get(
                f"{BASE_URL}/events", headers=headers, params=params
            )

            if response.status_code == 200:
                raw_data = response.json()
                events = get_events_list(raw_data)

                if events:
                    print(f"  -> Success: Retrieved {len(events)} events.")
                    for event in events:
                        if isinstance(event, dict):
                            event["_queried_actor"] = actor if actor else "Any"
                    all_events_data.extend(events)
                else:
                    print("  -> Success, but no event records were found.")

            elif response.status_code == 402:
                print("  -> Error 402: Insufficient credits or payment required.")
            else:
                print(f"  -> Error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  -> An error occurred while making the request: {e}")

        print("-" * 58)

    if not all_events_data:
        return None

    return pd.DataFrame(all_events_data)
