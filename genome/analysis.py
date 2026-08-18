"""Statistical analysis: summary stats, moving averages, cointegration."""

import itertools

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller

# A cointegration test on a handful of points is meaningless. Require a
# reasonable number of overlapping observations before trusting a result.
MIN_OBS_FOR_COINT = 30


def calculate_stats_and_ma(df, actor_countries):
    """Attach a 30-day moving average of weight per actor and return summary stats.

    For each actor a column `ma_weight_{actor}` is added to `df` holding the
    30-day rolling mean of that actor's daily event weight. A summary-statistics
    table (one row per actor) is printed and returned.
    """
    stats_dict = {}

    for actor in actor_countries:
        mask = df["_queried_actor"] == actor
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
        return stats_df

    return df


def _is_stationary(series, alpha=0.05):
    """ADF unit-root test. Returns True if the series looks stationary (I(0))."""
    series = series.dropna()
    if len(series) < MIN_OBS_FOR_COINT:
        return None  # not enough data to judge
    try:
        pvalue = adfuller(series, autolag="AIC")[1]
        return pvalue < alpha
    except Exception:
        return None


def run_cointegration_test(df, actor_countries):
    """Test each country pair for a shared long-term trend (cointegration).

    Engle-Granger cointegration assumes both daily-weight series are I(1)
    (non-stationary in levels). We therefore ADF-test each series first and skip
    pairs that don't meet the assumption. Because we test many pairs, raw
    p-values are also adjusted with a Benjamini-Hochberg (FDR) correction and
    both are reported.
    """
    print("\n\n--- Cointegration Test Results ---")
    print("(adjusted p-value < 0.05 suggests a shared long-term trend)\n")

    if len(actor_countries) < 2:
        print("Requires at least 2 countries to perform cointegration.")
        return

    # Build one daily weight series per actor.
    daily_series = {}
    for actor in actor_countries:
        mask = df["_queried_actor"] == actor
        actor_daily = (
            df[mask].groupby(df.loc[mask, "event_date"].dt.date)["weight"].mean()
        )
        actor_daily.index = pd.to_datetime(actor_daily.index)
        daily_series[actor] = actor_daily

    country_pairs = list(itertools.combinations(actor_countries, 2))

    results = []  # (c1, c2, raw_p)
    for c1, c2 in country_pairs:
        pair_df = pd.DataFrame({c1: daily_series[c1], c2: daily_series[c2]})
        # Only use days where both actually have events; do not invent zeros.
        pair_df = pair_df.dropna()

        if len(pair_df) < MIN_OBS_FOR_COINT:
            print(f"  ~ {c1} & {c2}: not enough overlapping days "
                  f"({len(pair_df)} < {MIN_OBS_FOR_COINT}).")
            continue

        s1_stat = _is_stationary(pair_df[c1])
        s2_stat = _is_stationary(pair_df[c2])
        if s1_stat or s2_stat:
            # If either series is already stationary, Engle-Granger doesn't apply.
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
        print(f"  {c1} & {c2}: {verdict} "
              f"(raw p={p:.4f}, adj p={adj_p:.4f})")
