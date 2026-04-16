"""
High-level data fetch helpers built on top of dhan_api.

Provides:
  ist_now()            — current datetime in IST
  is_market_open()     — True during NSE trading hours
  fetch_intraday_ohlcv() — batch 15-min OHLCV for a list of symbols
  fetch_ath()          — batch 5-yr ATH for a list of symbols
"""

import logging
import time
from datetime import datetime, timedelta, date
from typing import Callable

import pandas as pd

from config.settings import CONFIG, IST, MARKET_OPEN, MARKET_CLOSE
from data.dhan_api import fetch_intraday, fetch_historical

logger = logging.getLogger(__name__)


def ist_now() -> datetime:
    return datetime.now(IST)


def is_market_open() -> bool:
    now = ist_now()
    if now.weekday() >= 5:
        return False
    return MARKET_OPEN <= (now.hour, now.minute) <= MARKET_CLOSE


def fetch_intraday_ohlcv(
    symbols:        list[str],
    seg_fn:         Callable[[str], str],
    inst_fn:        Callable[[str], str],
    sid_fn:         Callable[[str], str | None],
    days_back:      int,
) -> dict[str, pd.DataFrame]:
    """
    Fetch 15-min OHLCV for every symbol in *symbols*.

    Args:
        symbols:   Trading symbols to fetch.
        seg_fn:    symbol → exchange segment string.
        inst_fn:   symbol → instrument type string.
        sid_fn:    symbol → Dhan security_id string (or None if unknown).
        days_back: How many calendar days of history to request.

    Returns:
        dict mapping symbol → DataFrame (skips symbols with no data).
    """
    to_dt   = datetime.now()
    from_dt = to_dt - timedelta(days=days_back)
    result: dict[str, pd.DataFrame] = {}

    for sym in symbols:
        sid = sid_fn(sym)
        if not sid:
            logger.debug("No security_id for %s — skipping", sym)
            continue
        df = fetch_intraday(sid, seg_fn(sym), inst_fn(sym), from_dt, to_dt)
        if df is not None and len(df) >= 5:
            result[sym] = df
        time.sleep(CONFIG["api_call_delay_secs"])

    return result


def fetch_ath(
    symbols:  list[str],
    seg_fn:   Callable[[str], str],
    inst_fn:  Callable[[str], str],
    sid_fn:   Callable[[str], str | None],
) -> dict[str, float]:
    """
    Fetch 5-year ATH (all-time high) for every symbol in *symbols*.

    Returns:
        dict mapping symbol → ATH float (skips symbols with no data).
    """
    from_date = date.today() - timedelta(days=int(CONFIG["ath_lookback_years"] * 365.25))
    to_date   = date.today()
    result: dict[str, float] = {}

    for sym in symbols:
        sid = sid_fn(sym)
        if not sid:
            continue
        highs = fetch_historical(sid, seg_fn(sym), inst_fn(sym), from_date, to_date)
        if highs is not None and len(highs) > 0:
            result[sym] = float(highs.max())
        time.sleep(CONFIG["api_call_delay_secs"])

    return result
