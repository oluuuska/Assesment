"""Cleaning and feature engineering for GENOME event data."""

import pandas as pd

from genome.config import EVENT_WEIGHTS


def process_event_data(df):
    """Clean the raw events DataFrame and attach a signed intensity weight.

    Adds:
        event_date : parsed datetime
        weight     : signed EVENT_WEIGHTS value for the event_type

    Rows with an unparseable date are dropped. Event types not present in
    EVENT_WEIGHTS are reported (so they are never dropped silently) and left
    as NaN weights.
    """
    if "event_date" not in df.columns or "event_type" not in df.columns:
        print(
            "\nMissing required columns ('event_date' or 'event_type') "
            "in API response. Exiting."
        )
        return None

    # Surface any event types we don't have a weight for, rather than letting
    # them vanish into NaN unnoticed.
    unmapped = sorted(set(df["event_type"].dropna()) - set(EVENT_WEIGHTS))
    if unmapped:
        print(f"  ! Warning: unmapped event types (weight=NaN): {unmapped}")

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["weight"] = df["event_type"].map(EVENT_WEIGHTS)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    df = df.dropna(subset=["event_date"])
    return df
