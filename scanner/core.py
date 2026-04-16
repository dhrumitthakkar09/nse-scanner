"""
Pure scanner calculations — no I/O, no side effects.

Every function here is deterministic given the same inputs, which
makes them straightforward to unit-test independently.
"""

import numpy as np
import pandas as pd

from config.settings import CONFIG


def resample75(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample a 15-min OHLCV DataFrame to 75-min candles aligned
    to the NSE session open (09:15 IST).

    Args:
        df: DataFrame with columns [Open, High, Low, Close, Volume]
            and a DatetimeIndex (tz-aware or tz-naive).

    Returns:
        Resampled DataFrame; rows with any NaN dropped.
    """
    df = df.copy()
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Kolkata")
    else:
        df.index = df.index.tz_convert("Asia/Kolkata")

    return (
        df.resample(
            f"{CONFIG['resample_minutes']}min",
            offset="9H15min",
        )
        .agg(
            {
                "Open":   "first",
                "High":   "max",
                "Low":    "min",
                "Close":  "last",
                "Volume": "sum",
            }
        )
        .dropna()
    )


def near_ath(price: float, ath: float) -> tuple[bool, float | None]:
    """
    Check whether *price* is within the configured ATH band.

    Returns:
        (qualifies, distance_pct) where distance_pct = (ath-price)/ath*100.
        distance_pct is None when ath is invalid.
    """
    if not ath or np.isnan(ath) or ath <= 0:
        return False, None
    dist = (ath - price) / ath * 100
    qualifies = CONFIG["ath_min_dist_pct"] <= dist <= CONFIG["ath_max_dist_pct"]
    return qualifies, round(dist, 2)


def is_consolidating(
    high: pd.Series,
    low:  pd.Series,
    n:    int,
    max_range_pct: float,
) -> tuple[bool, float | None]:
    """
    Check whether the last *n* candles form a tight consolidation.

    Returns:
        (qualifies, range_pct) where range_pct = (max_high - min_low) / min_low * 100.
    """
    if len(high) < n:
        return False, None
    rng   = high.iloc[-n:].max() - low.iloc[-n:].min()
    range_pct = rng / low.iloc[-n:].min() * 100
    return range_pct <= max_range_pct, round(range_pct, 2)


def avg_volume(vol: pd.Series, n: int = 20) -> float:
    """Average volume over the last *n* candles (min 5 candles required)."""
    if len(vol) < 5:
        return 0.0
    return float(vol.iloc[-min(n, len(vol)):].mean())


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential moving average with span = *period*."""
    return series.ewm(span=period, adjust=False).mean()
