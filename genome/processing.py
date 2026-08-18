"""Cleaning and feature engineering for GENOME event data."""

import pandas as pd

from genome.config import EVENT_WEIGHTS


def process_event_data(df):
    """Clean the raw events DataFrame and attach a signed intensity weight.

    Adds:
        event_date : parsed datetime
        weight     : signed EVENT_WEIGHTS value for the event_type

    Rows with an unparseable date are dropped. Blank / 'NaN' event types are
    normalised away first, and any event type not present in EVENT_WEIGHTS is
    reported (never dropped silently) and left as a NaN weight.
    """
    if "event_date" not in df.columns or "event_type" not in df.columns:
        print(
            "\nMissing required columns ('event_date' or 'event_type') "
            "in API response. Exiting."
        )
        return None

    df = df.copy()

    # Normalise the event_type: strip whitespace, uppercase, and turn the
    # literal strings '' and 'NAN' into a real missing value.
    df["event_type"] = (
        df["event_type"].astype(str).str.strip().str.upper()
    )
    df["event_type"] = df["event_type"].replace({"": pd.NA, "NAN": pd.NA})

    # Surface any *real* event types we don't have a weight for.
    known = set(EVENT_WEIGHTS)
    present = set(df["event_type"].dropna())
    unmapped = sorted(present - known)
    if unmapped:
        print(f"  ! Warning: unmapped event types (weight=NaN): {unmapped}")

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["weight"] = df["event_type"].map(EVENT_WEIGHTS)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    # Drop rows we can't place in time or score.
    df = df.dropna(subset=["event_date", "weight"])
    return df
