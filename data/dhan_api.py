"""
Raw Dhan HQ API calls.

Thin HTTP wrappers — no business logic. Each function returns
a pandas object on success or None on any failure, so callers
never need to catch HTTP exceptions.

Docs: https://dhanhq.co/docs/v2/
"""

import logging
from datetime import datetime, date

import pandas as pd
import requests

from config.settings import CREDENTIALS, DHAN_BASE

logger = logging.getLogger(__name__)


def _headers() -> dict:
    return {
        "access-token": CREDENTIALS["dhan_access_token"],
        "client-id":    CREDENTIALS["dhan_client_id"],
        "Content-Type": "application/json",
        "Accept":       "application/json",
    }


def fetch_intraday(
    security_id: str,
    exchange_seg: str,
    instrument: str,
    from_dt: datetime,
    to_dt: datetime,
    interval: int = 15,
) -> pd.DataFrame | None:
    """
    Fetch intraday OHLCV candles.

    Args:
        security_id:  Dhan numeric security ID (as string).
        exchange_seg: e.g. "NSE_EQ" or "IDX_I".
        instrument:   "EQUITY" or "INDEX".
        from_dt:      Start datetime (naive local or timezone-aware).
        to_dt:        End datetime.
        interval:     Candle size in minutes. Supported: 1, 5, 15, 25, 60.

    Returns:
        DataFrame with columns [Open, High, Low, Close, Volume]
        and a timezone-aware (Asia/Kolkata) DatetimeIndex, or None.
    """
    payload = {
        "securityId":      str(security_id),
        "exchangeSegment": exchange_seg,
        "instrument":      instrument,
        "interval":        str(interval),
        "fromDate":        from_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "toDate":          to_dt.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        r = requests.post(
            f"{DHAN_BASE}/charts/intraday",
            json=payload,
            headers=_headers(),
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        if not data or "open" not in data or not data.get("open"):
            return None
        idx = pd.to_datetime(
            [datetime.fromtimestamp(ts) for ts in data["timestamp"]]
        ).tz_localize("Asia/Kolkata")
        df = pd.DataFrame(
            {
                "Open":   data["open"],
                "High":   data["high"],
                "Low":    data["low"],
                "Close":  data["close"],
                "Volume": data["volume"],
            },
            index=idx,
        )
        return df.sort_index()
    except Exception as exc:
        logger.warning("Intraday fetch failed for %s: %s", security_id, exc)
        return None


def fetch_historical(
    security_id: str,
    exchange_seg: str,
    instrument: str,
    from_date: date,
    to_date: date,
) -> pd.Series | None:
    """
    Fetch daily high prices from Dhan historical endpoint.

    Returns:
        pd.Series of High values with DatetimeIndex, or None.
    """
    payload = {
        "securityId":      str(security_id),
        "exchangeSegment": exchange_seg,
        "instrument":      instrument,
        "fromDate":        from_date.strftime("%Y-%m-%d"),
        "toDate":          to_date.strftime("%Y-%m-%d"),
        "expiryCode":      0,
    }
    try:
        r = requests.post(
            f"{DHAN_BASE}/charts/historical",
            json=payload,
            headers=_headers(),
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        if not data or "high" not in data or not data.get("high"):
            return None
        idx = pd.to_datetime(
            [datetime.fromtimestamp(ts) for ts in data["timestamp"]]
        )
        return pd.Series(data["high"], index=idx)
    except Exception as exc:
        logger.warning("Historical fetch failed for %s: %s", security_id, exc)
        return None
