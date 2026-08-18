"""Statistical analysis: summary stats, moving averages, cointegration."""

import itertools

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller

# A cointegration test on a handful of points is meaningless. Require a
# reasonable number of overlapping observations before trusting a result.
MIN_OBS_FOR_COINT = 30

ACTOR_COL = "_queried_actor"


def _resolve_actors(df, actor_countries):
    """Return the actors we can actually analyse, with clear diagnostics.

    Guards against the two things that used to crash the pipeline:
    a missing actor column, and requested actors that aren't in the data.
    """
    if ACTOR_COL not in df.columns:
        print(f"  ! '{ACTOR_COL}' column not found; cannot run per-actor "
              f"analysis. Available columns: {list(df.columns)}")
        return []

    available = set(df[ACTOR_COL].dropna().unique())
    requested = [a for a in actor_countries if a]  # drop blanks
    usable = [a for a in requested if a in available]

    missing = [a for a in requested if a not in available]
    if missing:
        print(f"  ! No events for: {missing}. "
              f"Actors present in data: {sorted(available)}")

    return usable


def calculate_stats_and_ma(df, actor_countries):
    """Attach a 30-day moving average of weight per actor and print summary stats."""
    actors = _resolve_actors(df, actor_countries)
    stats_dict = {}

    for actor in actors:
        mask = df[ACTOR_COL] == actor
        sub_df = df[mask].copy()

        ma_col_name = f"ma_weight_{actor}"
        df[ma_col_name] = np.nan

        if not sub_df.empty:
            sub_df = sub_df.sort_values("event_date")
            roll = (
                sub_df.set_index("event_date")
                .rolling("30D", min_periods=1)["weight"]
                .mean()
            )
            sub_df[ma_col_name] = roll.values
            df.loc[sub_df.index, ma_col_name] = sub_df[ma_col_name]

        country_weights = df.loc[mask, "weight"].dropna()
        if not country_weights.empty:
            stats_dict[actor] = country_weights.describe()

    if stats_dict:
        stats_df = pd.DataFrame(stats_dict).T
        print("\n--- Summary Statistics of 'weight' by Country ---\n")
        print(stats_df.round(2))

    return df


def _is_stationary(series, alpha=0.05):
    """ADF unit-root test. Returns True if the series looks stationary (I(0))."""
    series = series.dropna()
    if len(series) < MIN_OBS_FOR_COINT:
        return None
    try:
        pvalue = adfuller(series, autolag="AIC")[1]
        return pvalue < alpha
    except Exception:
        return None


def run_cointegration_test(df, actor_countries):
    """Test each country pair for a shared long-term trend (cointegration)."""
    print("\n\n--- Cointegration Test Results ---")
    print("(adjusted p-value < 0.05 suggests a shared long-term trend)\n")

    actors = _resolve_actors(df, actor_countries)
    if len(actors) < 2:
        print("Requires at least 2 countries with data to run cointegration.")
        return

    daily_series = {}
    for actor in actors:
        mask = df[ACTOR_COL] == actor
        actor_daily = (
            df[mask].groupby(df.loc[mask, "event_date"].dt.date)["weight"].mean()
        )
        actor_daily.index = pd.to_datetime(actor_daily.index)
        daily_series[actor] = actor_daily

    results = []
    for c1, c2 in itertools.combinations(actors, 2):
        pair_df = pd.DataFrame({c1: daily_series[c1], c2: daily_series[c2]}).dropna()

        if len(pair_df) < MIN_OBS_FOR_COINT:
            print(f"  ~ {c1} & {c2}: not enough overlapping days "
                  f"({len(pair_df)} < {MIN_OBS_FOR_COINT}).")
            continue

        if _is_stationary(pair_df[c1]) or _is_stationary(pair_df[c2]):
            print(f"  ~ {c1} & {c2}: skipped (a series is stationary; "
                  f"cointegration assumption not met).")
            continue

        try:
            _, p_value, _ = coint(pair_df[c1], pair_df[c2])
            results.append((c1, c2, p_value))
        except Exception as e:
            print(f"  ~ {c1} & {c2}: test failed ({e}).")

    if not results:
        print("No pairs met the requirements for a valid cointegration test.")
        return

    # Benjamini-Hochberg FDR correction across all tested pairs.
    results.sort(key=lambda r: r[2])
    m = len(results)
    for rank, (c1, c2, p) in enumerate(results, start=1):
        adj_p = min(p * m / rank, 1.0)
        verdict = "MATCH" if adj_p < 0.05 else "no shared trend"
        print(f"  {c1} & {c2}: {verdict} (raw p={p:.4f}, adj p={adj_p:.4f})")
