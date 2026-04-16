"""
Scan orchestrator — coordinates all data fetching, applies scan logic,
updates shared state, and drives the background scheduler.

Imports pure functions from scanner.core and data helpers from data.*
so this module stays thin: no HTTP calls, no HTML, no Flask.
"""

import logging
import threading
import time
from datetime import timedelta

import pandas as pd

from config.sectors import SECTOR_INDICES
from config.settings import CONFIG
from config.stocks import ALL_STOCKS, STOCK_SECTOR_MAP
from data import fetcher, scrip_master
from scanner import alerts
from scanner.core import avg_volume, ema, is_consolidating, near_ath, resample75

logger = logging.getLogger(__name__)

# ── Shared state (read by Flask routes via /api/data) ─────────────
state: dict = dict(
    status="idle",
    last_scan=None,
    next_scan=None,
    sectors=[],
    stocks=[],
    intraday_stocks=[],
    scan_count=0,
    market_open=False,
    log=[],
)
_lock           = threading.Lock()
_prev_qualified: set | None = None   # None = skip first-scan Telegram alert


# ── Internal logger (writes to state["log"] + stdout) ─────────────
def _log(msg: str) -> None:
    ts   = fetcher.ist_now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with _lock:
        state["log"].append(line)
        if len(state["log"]) > 80:
            state["log"] = state["log"][-80:]
    print(line)


# ── Dhan lookup helpers ────────────────────────────────────────────
def _eq_seg(sym: str)  -> str:       return (scrip_master.equity_info(sym) or {}).get("exchange_seg", "NSE_EQ")
def _eq_ins(sym: str)  -> str:       return (scrip_master.equity_info(sym) or {}).get("instrument",   "EQUITY")
def _eq_sid(sym: str)  -> str | None: return (scrip_master.equity_info(sym) or {}).get("security_id")

def _idx_seg(name: str) -> str:       return (scrip_master.index_info(name) or {}).get("exchange_seg", "IDX_I")
def _idx_ins(name: str) -> str:       return (scrip_master.index_info(name) or {}).get("instrument",   "INDEX")
def _idx_sid(name: str) -> str | None: return (scrip_master.index_info(name) or {}).get("security_id")


# ── Main scan ─────────────────────────────────────────────────────
def run_scan() -> None:
    global _prev_qualified
    scrip_master.ensure()

    with _lock:
        state["status"]      = "scanning"
        state["market_open"] = fetcher.is_market_open()
        state["scan_count"] += 1
    _log("▶ Scan started (Dhan API)")

    try:
        idx_names = list(SECTOR_INDICES.values())

        # ── 1/4  Sector ATH (5-yr daily) ──────────────────────────
        _log("1/4 — Sector ATH (5-yr daily)…")
        ath_s = fetcher.fetch_ath(
            idx_names, _idx_seg, _idx_ins, _idx_sid,
        )

        # ── 2/4  Sector intraday → 75-min ─────────────────────────
        _log("2/4 — Sector intraday (15-min → 75-min)…")
        raw_s = fetcher.fetch_intraday_ohlcv(
            idx_names, _idx_seg, _idx_ins, _idx_sid,
            days_back=CONFIG["intraday_lookback_days"],
        )

        sectors = []
        for sec, idx_name in SECTOR_INDICES.items():
            ath = ath_s.get(idx_name)
            if idx_name not in raw_s or not ath:
                sectors.append(dict(sector=sec, symbol=idx_name,
                                    ath=None, price=None, dist_pct=None, trending=False))
                continue
            try:
                c     = resample75(raw_s[idx_name])
                price = float(c["Close"].iloc[-1])
                q, d  = near_ath(price, ath)
                sectors.append(dict(sector=sec, symbol=idx_name,
                                    ath=round(ath, 2), price=round(price, 2),
                                    dist_pct=d, trending=q))
            except Exception:
                sectors.append(dict(sector=sec, symbol=idx_name,
                                    ath=None, price=None, dist_pct=None, trending=False))

        sectors.sort(key=lambda x: (x["dist_pct"] is None, x["dist_pct"] or 999))
        trending = {s["sector"] for s in sectors if s["trending"]}
        _log(f"   Trending sectors: {', '.join(sorted(trending)) or 'none'}")

        # ── Intraday % change for each sector (today open→close) ──
        _now       = fetcher.ist_now()
        _day_start = _now.replace(hour=9,  minute=15, second=0, microsecond=0)
        _day_end   = _now.replace(hour=15, minute=30, second=0, microsecond=0)

        def _today_candles(df: pd.DataFrame) -> pd.DataFrame:
            """Return the candles that fall within today's NSE session."""
            idx = df.index
            if idx.tz is None:
                idx = idx.tz_localize("Asia/Kolkata")
            else:
                idx = idx.tz_convert("Asia/Kolkata")
            df = df.copy()
            df.index = idx
            return df[(df.index >= _day_start) & (df.index <= _day_end)]

        for sec_d in sectors:
            idx_name = sec_d["symbol"]
            try:
                if idx_name in raw_s:
                    tod = _today_candles(raw_s[idx_name])
                    if len(tod) >= 1:
                        op = float(tod["Open"].iloc[0])
                        cl = float(tod["Close"].iloc[-1])
                        sec_d["intraday_chg"] = round((cl - op) / op * 100, 2) if op > 0 else None
                    else:
                        sec_d["intraday_chg"] = None
                else:
                    sec_d["intraday_chg"] = None
            except Exception:
                sec_d["intraday_chg"] = None

        # ── 3/4  Stock ATH ────────────────────────────────────────
        cands = [t for t in ALL_STOCKS if STOCK_SECTOR_MAP.get(t, "") in trending] or ALL_STOCKS
        _log(f"3/4 — Stock ATH for {len(cands)} stocks…")
        ath_k = fetcher.fetch_ath(cands, _eq_seg, _eq_ins, _eq_sid)

        # ── 4/4  Stock intraday data (all stocks for intraday; cands for consolidation) ─
        _log(f"4/4 — Stock intraday scan ({len(ALL_STOCKS)} F&O stocks)…")
        raw_k = fetcher.fetch_intraday_ohlcv(
            ALL_STOCKS, _eq_seg, _eq_ins, _eq_sid,
            days_back=CONFIG["intraday_lookback_days"],
        )
        _log(f"   → {len(raw_k)} stocks with data")

        stocks = []
        for sym in cands:
            ath = ath_k.get(sym)
            if sym not in raw_k or not ath:
                continue
            try:
                c  = resample75(raw_k[sym])
                cl = c["Close"]; hi = c["High"]; lo = c["Low"]; vo = c["Volume"]
                if len(cl) < 10:
                    continue
                av = avg_volume(vo, 20)
                if av < CONFIG["min_avg_volume"]:
                    continue
                pr   = float(cl.iloc[-1])
                q, d = near_ath(pr, float(ath))
                if not q:
                    continue
                ok, rng = is_consolidating(hi, lo, CONFIG["consol_candles"], CONFIG["max_range_pct"])
                if not ok:
                    continue
                up = True
                if len(cl) >= CONFIG["ema_slow"]:
                    up = float(ema(cl, CONFIG["ema_fast"]).iloc[-1]) > \
                         float(ema(cl, CONFIG["ema_slow"]).iloc[-1])
                va  = avg_volume(vo, 10)
                vs  = round(float(vo.iloc[-1]) / va, 2) if va > 0 else 1.0
                ch  = round((float(cl.iloc[-1]) - float(cl.iloc[-6])) /
                            float(cl.iloc[-6]) * 100, 2) if len(cl) >= 6 else 0.0
                stocks.append(dict(
                    name=sym, sector=STOCK_SECTOR_MAP.get(sym, ""),
                    price=round(pr, 2), ath=round(float(ath), 2),
                    dist_pct=d, range_pct=rng, chg_1d=ch,
                    vol_surge=vs, uptrend=up,
                ))
            except Exception:
                pass

        stocks.sort(key=lambda x: x["dist_pct"])

        # ── Intraday change for ALL fetched stocks ────────────────
        intraday_stocks = []
        for sym in raw_k:
            try:
                tod = _today_candles(raw_k[sym])
                if len(tod) < 1:
                    continue
                op = float(tod["Open"].iloc[0])
                cl = float(tod["Close"].iloc[-1])
                if op <= 0:
                    continue
                intraday_stocks.append(dict(
                    name=sym,
                    sector=STOCK_SECTOR_MAP.get(sym, ""),
                    price=round(cl, 2),
                    intraday_chg=round((cl - op) / op * 100, 2),
                ))
            except Exception:
                pass
        intraday_stocks.sort(key=lambda x: x["intraday_chg"], reverse=True)
        _log(f"   → {len(intraday_stocks)} stocks with intraday data")

        # ── Telegram alert for new entries ────────────────────────
        current_names = {s["name"] for s in stocks}
        if _prev_qualified is not None:
            newly_in = [s for s in stocks if s["name"] not in _prev_qualified]
            if newly_in:
                _log(f"🔔 {len(newly_in)} new signal(s) — sending Telegram alert…")
                ts = fetcher.ist_now().strftime("%d %b %Y, %H:%M IST")
                alerts.send_new_signals(newly_in, ts)
        _prev_qualified = current_names

        # ── Update shared state ───────────────────────────────────
        now = fetcher.ist_now()
        with _lock:
            state.update(
                sectors=sectors,
                stocks=stocks,
                intraday_stocks=intraday_stocks,
                last_scan=now.strftime("%d %b %Y, %H:%M:%S IST"),
                next_scan=(now + timedelta(minutes=CONFIG["scan_interval_minutes"])).strftime("%H:%M IST"),
                status="done",
            )
        _log(f"✅ Done — {len(stocks)} stocks qualified")

    except Exception as exc:
        with _lock:
            state["status"] = "error"
        _log(f"❌ Error: {exc}")


# ── Background scheduler ──────────────────────────────────────────
def sched_loop() -> None:
    """Sleep for scan_interval_minutes, then spawn run_scan in its own thread.
    Reads CONFIG each cycle so settings changes take effect immediately.
    Runs the scan in a daemon thread so sched_loop never blocks.
    """
    while True:
        mins = CONFIG.get("scan_interval_minutes", 15)
        time.sleep(mins * 60)
        threading.Thread(target=run_scan, daemon=True).start()
