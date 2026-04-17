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
# Populated by load() — used by /api/scrip-debug for diagnostics
load_info:    dict = {}
# Built at load time: normalized-key → info for fuzzy fallback (O(1) lookup)
_NORM_MAP:    dict[str, dict] = {}

# Known symbol differences between our ALL_STOCKS list and Dhan CSV tickers.
SYMBOL_ALIASES: dict[str, str] = {
    # ── Confirmed from scrip-debug near-match output ──────────────────────────
    "APOLLOTYRE":  "APOLLO TYRES",
    "BALKRISIND":  "BALKRISHNA INDUSTRIES",
    "CEATLTD":     "CEAT",
    "CENTRALBK":   "CENTRAL BANK OF INDIA",
    "CREDITACC":   "CREDIT ACCESS GRAMEEN",
    "HOMEFIRST":   "HOME FIRST FINANCE COMPANY",
    "RATEGAIN":    "RATEGAIN TRAVEL",
    "SUNDARMFIN":  "SUNDARAM FINANCE",
    "UJJIVANSFB":  "UJJIVAN SMALL FINANCE BANK",
    # ── ZOMATO rebranded to Eternal Ltd on NSE in 2025 ───────────────────────
    "ZOMATO":      "ETERNAL",
    # ── Display-name suffix vs ticker mismatches ──────────────────────────────
    "CANFINHOME":  "CAN FIN HOMES",
    "CSBBANK":     "CSB BANK",
    "DCBBANK":     "DCB BANK",
    "IOB":         "INDIAN OVERSEAS BANK",
    "J&KBANK":     "JAMMU AND KASHMIR BANK",
    "LTIM":        "LTI MINDTREE",
    "M&MFIN":      "MAHINDRA AND MAHINDRA FINANCIAL",
    "MAHABANK":    "BANK OF MAHARASHTRA",
    "MAPMYINDIA":  "CE INFO SYSTEMS",
    "INDIAMART":   "INDIAMART INTERMESH",
    "KARURVYSYA":  "KARUR VYSYA BANK",
    # ── Other known Dhan display-name differences ─────────────────────────────
    "ZENSAR":      "ZENSAR TECHNOLOGIES",
    "MCDOWELL-N":  "MCDOWELL AND COMPANY",
    "BAJAJ-AUTO":  "BAJAJ AUTO",
    "M&M":         "MAHINDRA AND MAHINDRA",
    "INDIANB":     "INDIAN BANK",
    "UNIONBANK":   "UNION BANK OF INDIA",
    "IDFCFIRSTB":  "IDFC FIRST BANK",
    "BANDHANBNK":  "BANDHAN BANK",
    "FEDERALBNK":  "FEDERAL BANK",
    "BANKBARODA":  "BANK OF BARODA",
    "INDUSINDBK":  "INDUSIND BANK",
    "KOTAKBANK":   "KOTAK MAHINDRA BANK",
}

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
            logger.info("CSV: %d rows, %d cols", len(df), len(cols))
            logger.info("All columns: %s", sorted(cols))

            def _find(*cands: str) -> str | None:
                for c in cands:
                    if c in cols:
                        return c
                return None

            sid_col  = _find("SECURITY_ID", "SEM_SMST_SECURITY_ID", "SM_SMST_SECURITY_ID")
            exch_col = _find("SEM_EXM_EXCH_ID",       "EXCH_ID",        "SEM_EXCH_ID")
            seg_col  = _find("SEM_SEGMENT",            "SEGMENT")
            inst_col = _find("SEM_INSTRUMENT_NAME",    "INSTRUMENT",     "SM_INSTRUMENT_NAME")
            sym_col  = _find("SEM_TRADING_SYMBOL",     "SM_TRADING_SYMBOL",
                             "TRADING_SYMBOL",       "DISPLAY_NAME",
                             "SM_SYMBOL_NAME",       "SYMBOL_NAME")

            if not all([sid_col, exch_col, seg_col, inst_col, sym_col]):
                logger.warning(
                    "Scrip master: cannot detect required columns. "
                    "Columns found: %s", sorted(cols)[:20]
                )
                return

            # Capture column values for diagnostics (exposed via /api/scrip-debug)
            col_vals = {}
            for col in [exch_col, seg_col, inst_col]:
                top_vals = df[col].value_counts().head(10).index.tolist()
                col_vals[col] = top_vals
                logger.info("  Column %-24s top values: %s", col, top_vals)

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

            # ── Build equity map (two strategies, merged) ────────────────────────
            und_sym_col = "UNDERLYING_SYMBOL"      if "UNDERLYING_SYMBOL"      in cols else None
            und_sid_col = "UNDERLYING_SECURITY_ID" if "UNDERLYING_SECURITY_ID" in cols else None
            series_col  = "SERIES"                 if "SERIES"                 in cols else None

            # Strategy A — FUTSTK + OPTSTK underlying data.
            # UNDERLYING_SYMBOL = exact NSE ticker; UNDERLYING_SECURITY_ID = equity cash security_id.
            # Best for stocks actively traded in F&O.
            fno_equities: dict = {}
            if und_sym_col and und_sid_col:
                fno_df = (
                    df[
                        (df[exch_col] == "NSE")
                        & df[inst_col].isin(["FUTSTK", "OPTSTK"])
                    ]
                    [[und_sym_col, und_sid_col]]
                    .copy()
                    .dropna(subset=[und_sym_col])
                )
                fno_df[und_sym_col] = fno_df[und_sym_col].str.strip().str.upper()
                fno_df = fno_df.drop_duplicates(subset=[und_sym_col])
                for _, row in fno_df.iterrows():
                    sym = row[und_sym_col]
                    try:
                        sid = str(int(float(row[und_sid_col])))
                    except (ValueError, TypeError):
                        continue
                    if sym and sid not in ("0", "nan"):
                        fno_equities[sym] = {
                            "security_id":  sid,
                            "exchange_seg": "NSE_EQ",
                            "instrument":   "EQUITY",
                        }
                logger.info("Strategy A (FUTSTK+OPTSTK underlying): %d entries", len(fno_equities))

            # Strategy B — EQUITY rows filtered to SERIES=="EQ".
            # For EQ-series equities, DISPLAY_NAME IS the short NSE ticker (ZOMATO, DCBBANK…).
            # Catches stocks that have no futures/options (small-cap banks, newer listings).
            if series_col:
                eq_mask = (
                    (df[exch_col] == "NSE")
                    & (df[inst_col] == "EQUITY")
                    & (df[series_col] == "EQ")
                )
            else:
                eq_mask = (df[exch_col] == "NSE") & (df[inst_col] == "EQUITY")
            eq_parsed = _parse(eq_mask, "NSE_EQ", "EQUITY")
            logger.info("Strategy B (EQUITY+SERIES=EQ): %d entries", len(eq_parsed))

            # Merge: Strategy A takes priority (FUTSTK underlying is unambiguous)
            merged_eq = {**eq_parsed, **fno_equities}

            # Clear old data before rebuilding (critical for force_reload correctness)
            EQUITY_MAP.clear()
            INDEX_MAP.clear()
            _NORM_MAP.clear()

            # Normalise symbols: store both "HDFCBANK-EQ" and "HDFCBANK" as keys
            for sym, info in merged_eq.items():
                EQUITY_MAP[sym] = info
                if sym.endswith("-EQ"):
                    EQUITY_MAP[sym[:-3]] = info

            # Build fuzzy-lookup map: strip common company-name suffixes + spaces
            # so "Zomato Limited" → "ZOMATO", "DCB Bank Ltd" → "DCBBANK"
            _SUFFIXES = [
                " LIMITED", " LTD.", " LTD", " PRIVATE LIMITED", " PVT LTD",
                " BANK", " SMALL FINANCE BANK", " FINANCIAL SERVICES",
                " FINANCIAL", " TECHNOLOGIES", " TECHNOLOGY",
                " INDUSTRIES", " ENTERPRISES", " SOLUTIONS",
                " SERVICES", " PRODUCTS", " CORPORATION", " COMPANY",
            ]
            def _norm(s: str) -> str:
                s = s.strip().upper()
                for sfx in _SUFFIXES:
                    if s.endswith(sfx):
                        s = s[: -len(sfx)].strip()
                        break
                return s.replace(" ", "").replace(".", "").replace("&", "AND")

            for sym, info in EQUITY_MAP.items():
                nk = _norm(sym)
                if nk and nk not in _NORM_MAP:
                    _NORM_MAP[nk] = info

            idx_mask = (df[exch_col] == "NSE") & (df[inst_col] == "INDEX")
            if not idx_mask.any():
                idx_mask = df[inst_col].str.upper().str.contains("INDEX", na=False)
            INDEX_MAP.update(_parse(idx_mask, "IDX_I", "INDEX"))

            logger.info(
                "Scrip master loaded: %d equities (%d merged), %d indices",
                len(EQUITY_MAP), len(merged_eq), len(INDEX_MAP),
            )
            sample_eq  = list(EQUITY_MAP.keys())[:8]
            sample_idx = list(INDEX_MAP.keys())[:5]
            logger.info("Sample equity keys : %s", sample_eq)
            logger.info("Sample index  keys : %s", sample_idx)

            # Capture sample equity symbols so mismatches are easy to spot
            eq_df    = df[eq_mask]
            fno_syms = list(fno_equities.keys())[:10]
            sample_syms = fno_syms if fno_syms else eq_df[sym_col].dropna().unique()[:10].tolist()
            logger.info("Sample equity symbols: %s", sample_syms)

            # Store diagnostics for /api/scrip-debug
            load_info.update({
                "csv_rows":          len(df),
                "all_columns":       sorted(list(cols)),
                "exch_col":          exch_col,
                "seg_col":           seg_col,
                "inst_col":          inst_col,
                "sym_col":           sym_col,
                "series_col":        series_col,
                "col_values":        col_vals,
                "fno_eq_count":      len(fno_equities),
                "eq_series_count":   len(eq_parsed),
                "eq_merged_count":   len(merged_eq),
                "equity_map_size":   len(EQUITY_MAP),
                "index_map_size":    len(INDEX_MAP),
                "sample_eq_syms":    [str(s) for s in sample_syms],
            })
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
    Clears both maps before rebuilding so stale entries don't survive.
    """
    global _loaded
    # Reset flag outside load()'s lock so load() will re-enter
    _loaded = False
    load()


def equity_info(symbol: str) -> dict | None:
    """Return Dhan API params for an equity symbol, or None.
    Lookup order:
      1. Exact match in EQUITY_MAP
      2. Symbol + "-EQ" suffix
      3. Known alias (SYMBOL_ALIASES)
      4. Normalised fuzzy match (_NORM_MAP) — handles "Zomato Limited" → "ZOMATO"
    """
    key = symbol.upper()
    # 1 & 2 — direct
    result = EQUITY_MAP.get(key) or EQUITY_MAP.get(key + "-EQ")
    if result:
        return result
    # 3 — known alias
    alias = SYMBOL_ALIASES.get(key)
    if alias:
        result = EQUITY_MAP.get(alias.upper()) or EQUITY_MAP.get(alias.upper() + "-EQ")
        if result:
            return result
    # 4 — normalised fuzzy (strips company suffixes then removes spaces)
    _SUFFIXES_LOCAL = [
        " LIMITED", " LTD.", " LTD", " PRIVATE LIMITED", " PVT LTD",
        " BANK", " SMALL FINANCE BANK", " FINANCIAL SERVICES",
        " FINANCIAL", " TECHNOLOGIES", " TECHNOLOGY",
        " INDUSTRIES", " ENTERPRISES", " SOLUTIONS",
        " SERVICES", " PRODUCTS", " CORPORATION", " COMPANY",
    ]
    def _norm(s: str) -> str:
        s = s.strip().upper()
        for sfx in _SUFFIXES_LOCAL:
            if s.endswith(sfx):
                s = s[: -len(sfx)].strip()
                break
        return s.replace(" ", "").replace(".", "").replace("&", "AND")

    nk = _norm(key)
    return _NORM_MAP.get(nk)


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
