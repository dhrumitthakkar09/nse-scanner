"""
Dhan scrip master — symbol → security_id lookup tables.

Downloads the Dhan CSV once at startup, parses it, and populates
two module-level dicts that the rest of the app queries:

  EQUITY_MAP  symbol (e.g. "HDFCBANK")  → {security_id, exchange_seg, instrument}
  INDEX_MAP   name   (e.g. "NIFTY BANK") → {security_id, exchange_seg, instrument}

Call ensure() before first use; it is idempotent and thread-safe.
"""

import logging
import threading
from io import StringIO

import pandas as pd
import requests

from config.settings import SCRIP_MASTER_URL

logger = logging.getLogger(__name__)

EQUITY_MAP: dict[str, dict] = {}
INDEX_MAP:  dict[str, dict] = {}

_loaded = False
_load_lock = threading.Lock()


def load() -> None:
    """Download and parse the Dhan scrip master CSV."""
    global EQUITY_MAP, INDEX_MAP, _loaded

    with _load_lock:
        if _loaded:
            return
        try:
            logger.info("Downloading Dhan scrip master…")
            resp = requests.get(SCRIP_MASTER_URL, timeout=60)
            resp.raise_for_status()

            df   = pd.read_csv(StringIO(resp.text), low_memory=False)
            cols = set(df.columns)

            def _find(*cands: str) -> str | None:
                for c in cands:
                    if c in cols:
                        return c
                return None

            sid_col  = _find("SEM_SMST_SECURITY_ID", "SECURITY_ID",    "SM_SMST_SECURITY_ID")
            exch_col = _find("SEM_EXM_EXCH_ID",       "EXCH_ID",        "SEM_EXCH_ID")
            seg_col  = _find("SEM_SEGMENT",            "SEGMENT")
            inst_col = _find("SEM_INSTRUMENT_NAME",    "INSTRUMENT",     "SM_INSTRUMENT_NAME")
            sym_col  = _find("SEM_TRADING_SYMBOL",     "SYMBOL_NAME",    "SM_SYMBOL_NAME",
                             "SM_TRADING_SYMBOL")

            if not all([sid_col, exch_col, seg_col, inst_col, sym_col]):
                logger.warning(
                    "Scrip master: cannot detect required columns. "
                    "Columns found: %s", sorted(cols)[:20]
                )
                return

            def _parse(mask, exchange_seg: str, instrument_type: str) -> dict:
                out = {}
                for _, row in df[mask].iterrows():
                    sym = str(row[sym_col]).strip().upper()
                    try:
                        sid = str(int(float(row[sid_col])))
                    except (ValueError, TypeError):
                        continue
                    if sym and sid not in ("0", "nan"):
                        out[sym] = {
                            "security_id":  sid,
                            "exchange_seg": exchange_seg,
                            "instrument":   instrument_type,
                        }
                return out

            eq_mask = (
                (df[exch_col] == "NSE")
                & (df[seg_col] == "E")
                & (df[inst_col] == "EQUITY")
            )
            eq_parsed = _parse(eq_mask, "NSE_EQ", "EQUITY")
            # Normalise symbols: Dhan often uses "SYMBOL-EQ" format.
            # Store both the raw key AND the stripped version so lookups
            # like equity_info("HDFCBANK") work whether the CSV has
            # "HDFCBANK" or "HDFCBANK-EQ".
            eq_normalised = {}
            for sym, info in eq_parsed.items():
                eq_normalised[sym] = info
                if sym.endswith("-EQ"):
                    eq_normalised[sym[:-3]] = info   # "HDFCBANK-EQ" → also "HDFCBANK"
            EQUITY_MAP.update(eq_normalised)

            idx_mask = (df[exch_col] == "NSE") & (df[inst_col] == "INDEX")
            if not idx_mask.any():
                idx_mask = df[inst_col].str.upper().str.contains("INDEX", na=False)
            INDEX_MAP.update(_parse(idx_mask, "IDX_I", "INDEX"))

            logger.info(
                "Scrip master loaded: %d equities (%d raw), %d indices",
                len(EQUITY_MAP), len(eq_parsed), len(INDEX_MAP),
            )
            # Log a few sample keys so mismatches are easy to spot
            sample_eq  = list(EQUITY_MAP.keys())[:5]
            sample_idx = list(INDEX_MAP.keys())[:5]
            logger.info("Sample equity keys : %s", sample_eq)
            logger.info("Sample index  keys : %s", sample_idx)
        except Exception as exc:
            logger.warning("Scrip master load failed: %s", exc)
        finally:
            _loaded = True


def ensure() -> None:
    """Load scrip master if not already loaded (idempotent)."""
    if not _loaded:
        load()


def force_reload() -> None:
    """Reset the loaded flag and re-download the scrip master CSV.
    Useful when EQUITY_MAP appears empty or stale without restarting the app.
    """
    global _loaded
    with _load_lock:
        _loaded = False
    load()


def equity_info(symbol: str) -> dict | None:
    """Return Dhan API params for an equity symbol, or None.
    Tries the exact symbol first, then with a '-EQ' suffix appended,
    to handle both Dhan CSV formats ('HDFCBANK' and 'HDFCBANK-EQ').
    """
    key = symbol.upper()
    return EQUITY_MAP.get(key) or EQUITY_MAP.get(key + "-EQ")


def index_info(name: str) -> dict | None:
    """
    Return Dhan API params for a sector index name, or None.
    Tries exact match first, then partial substring match.
    """
    key = name.upper()
    if key in INDEX_MAP:
        return INDEX_MAP[key]
    for k, v in INDEX_MAP.items():
        if key in k or k in key:
            return v
    return None
