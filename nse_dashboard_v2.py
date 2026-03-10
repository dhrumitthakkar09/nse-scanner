"""
╔══════════════════════════════════════════════════════════════════╗
║   NSE F&O CONSOLIDATION SCANNER  —  WEB DASHBOARD  v2          ║
║   220 F&O Stocks  |  75-Min candles  |  Scans every 15 mins    ║
╚══════════════════════════════════════════════════════════════════╝
Install:
    pip install yfinance pandas numpy pytz schedule flask

Run:
    python nse_dashboard.py

Open:  http://localhost:5050
"""

import warnings; warnings.filterwarnings("ignore")
import time, threading, pytz, schedule, yfinance as yf
import pandas as pd, numpy as np
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string

# ─────────────────────────────────────────────────────────────────
CONFIG = {
    "base_interval":          "15m",
    "resample_minutes":       75,
    "intraday_lookback_days": 50,
    "ath_lookback_years":     5,
    "ath_min_dist_pct":       0.0,
    "ath_max_dist_pct":       15.0,
    "consol_candles":         8,
    "max_range_pct":          5.0,
    "min_avg_volume":         200_000,
    "ema_fast":               9,
    "ema_slow":               21,
    "scan_interval_minutes":  15,
    "batch_size":             25,
    "batch_pause_secs":       2,
}
IST = pytz.timezone("Asia/Kolkata")
MARKET_OPEN  = (9, 15)
MARKET_CLOSE = (15, 30)

# ─────────────────────────────────────────────────────────────────
#  SECTOR INDICES
# ─────────────────────────────────────────────────────────────────
SECTOR_INDICES = {
    "IT":             "^CNXIT",
    "Bank":           "^NSEBANK",
    "Financial Svcs": "^CNXFIN",
    "Auto":           "^CNXAUTO",
    "Pharma":         "^CNXPHARMA",
    "FMCG":           "^CNXFMCG",
    "Metal":          "^CNXMETAL",
    "Energy":         "^CNXENERGY",
    "Realty":         "^CNXREALTY",
    "Infra":          "^CNXINFRA",
    "Media":          "^CNXMEDIA",
    "PSU Bank":       "^CNXPSUBANK",
}

# ─────────────────────────────────────────────────────────────────
#  ALL 220 NSE F&O STOCKS  (with sector mapping)
# ─────────────────────────────────────────────────────────────────
FNO_STOCKS = {
    # ── IT / Technology ──────────────────────────────────────────
    "IT": [
        "TCS.NS","INFY.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","LTI.NS",
        "LTIM.NS","MPHASIS.NS","COFORGE.NS","PERSISTENT.NS","TATAELXSI.NS",
        "OFSS.NS","HEXAWARE.NS","KPITTECH.NS","ZENSAR.NS","NIITTECH.NS",
        "RATEGAIN.NS","ZOMATO.NS","NAUKRI.NS","INDIAMART.NS","MAPMYINDIA.NS",
    ],
    # ── Banking ───────────────────────────────────────────────────
    "Bank": [
        "HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS",
        "INDUSINDBK.NS","BANKBARODA.NS","FEDERALBNK.NS","IDFCFIRSTB.NS",
        "RBLBANK.NS","BANDHANBNK.NS","KARURVYSYA.NS","DCBBANK.NS",
        "CSBBANK.NS","UJJIVANSFB.NS",
    ],
    # ── PSU Bank ─────────────────────────────────────────────────
    "PSU Bank": [
        "CANBK.NS","PNB.NS","UNIONBANK.NS","MAHABANK.NS","CENTRALBK.NS",
        "IOB.NS","INDIANB.NS","J&KBANK.NS",
    ],
    # ── Financial Services ───────────────────────────────────────
    "Financial Svcs": [
        "BAJFINANCE.NS","BAJAJFINSV.NS","CHOLAFIN.NS","SBICARD.NS",
        "SHRIRAMFIN.NS","HDFCLIFE.NS","SBILIFE.NS","ICICIGI.NS",
        "ICICIPRULI.NS","RECLTD.NS","IRFC.NS","POLICYBZR.NS",
        "MUTHOOTFIN.NS","MANAPPURAM.NS","LIChousing.NS","PNBHOUSING.NS",
        "ABCAPITAL.NS","IIFL.NS","M&MFIN.NS","SUNDARMFIN.NS",
        "CANFINHOME.NS","HOMEFIRST.NS","CREDITACC.NS","PAISALO.NS",
    ],
    # ── Auto ─────────────────────────────────────────────────────
    "Auto": [
        "MARUTI.NS","TATAMOTORS.NS","M&M.NS","BAJAJ-AUTO.NS","EICHERMOT.NS",
        "HEROMOTOCO.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
        "BALKRISIND.NS","APOLLOTYRE.NS","CEATLTD.NS","MRF.NS","TIINDIA.NS",
        "ENDURANCE.NS","SUPRAJIT.NS","SUNDRMFAST.NS","WABCOINDIA.NS",
        "TVSMOTOR.NS","ASHOKLEY.NS",
    ],
    # ── Pharma / Healthcare ──────────────────────────────────────
    "Pharma": [
        "SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","AUROPHARMA.NS",
        "LUPIN.NS","TORNTPHARM.NS","APOLLOHOSP.NS","ALKEM.NS","BIOCON.NS",
        "GLENMARK.NS","IPCA.NS","NATCOPHARM.NS","GRANULES.NS","LAURUSLABS.NS",
        "PFIZER.NS","ABBOTINDIA.NS","GLAXO.NS","STAR.NS","FORTIS.NS",
        "METROPOLIS.NS","THYROCARE.NS","MAXHEALTH.NS",
    ],
    # ── FMCG / Consumer ──────────────────────────────────────────
    "FMCG": [
        "HINDUNILVR.NS","ITC.NS","NESTLEIND.NS","TITAN.NS","BRITANNIA.NS",
        "TATACONSUM.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","PGHH.NS",
        "UBL.NS","MCDOWELL-N.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS",
        "DABUR.NS","EMAMILTD.NS","VBL.NS","JYOTHYLAB.NS","ZYDUSWELL.NS",
        "RADICO.NS","TATAPOWER.NS","GILLETTE.NS",
    ],
    # ── Metal / Mining ───────────────────────────────────────────
    "Metal": [
        "TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","VEDL.NS","COALINDIA.NS",
        "SRF.NS","SAIL.NS","NMDC.NS","NATIONALUM.NS","HINDCOPPER.NS",
        "RATNAMANI.NS","WELCORP.NS","APLAPOLLO.NS","JSWENERGY.NS",
        "MOIL.NS","GMRINFRA.NS",
    ],
    # ── Energy / Oil & Gas ───────────────────────────────────────
    "Energy": [
        "RELIANCE.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","BPCL.NS",
        "GAIL.NS","TATAPOWER.NS","ADANIGREEN.NS","NHPC.NS","ADANITRANS.NS",
        "ADANIENT.NS","IOC.NS","HINDPETRO.NS","PETRONET.NS","GUJGASLTD.NS",
        "IGL.NS","MGL.NS","CESC.NS","TORNTPOWER.NS","JSPL.NS",
    ],
    # ── Realty ───────────────────────────────────────────────────
    "Realty": [
        "DLF.NS","LODHA.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS",
        "BRIGADE.NS","SOBHA.NS","PHOENIXLTD.NS","SUNTEK.NS",
    ],
    # ── Infra / Capital Goods ────────────────────────────────────
    "Infra": [
        "LT.NS","ABB.NS","SIEMENS.NS","BEL.NS","ADANIPORTS.NS",
        "INDUSTOWER.NS","IRCTC.NS","HAVELLS.NS","VOLTAS.NS","ULTRACEMCO.NS",
        "AMBUJACEM.NS","GRASIM.NS","DELHIVERY.NS","BHARTIARTL.NS",
        "CUMMINSIND.NS","THERMAX.NS","BHEL.NS","IRCON.NS","RVNL.NS",
        "NBCC.NS","HFCL.NS","RAILVIKAS.NS","PFC.NS","HUDCO.NS",
    ],
    # ── Media / Telecom ──────────────────────────────────────────
    "Media": [
        "ZEEL.NS","SUNTV.NS","PVRINOX.NS","NETWORK18.NS","TV18BRDCST.NS",
    ],
    # ── Chemicals ────────────────────────────────────────────────
    "Chemicals": [
        "PIDILITIND.NS","DEEPAKNTR.NS","AARTIIND.NS","NAVINFLUOR.NS",
        "FLUOROCHEM.NS","CLEAN.NS","TATACHEM.NS","GSFC.NS","GNFC.NS",
        "CHAMBLFERT.NS","COROMANDEL.NS","PIIND.NS","RALLIS.NS",
    ],
    # ── Textiles / Misc ──────────────────────────────────────────
    "Textiles": [
        "PAGEIND.NS","RAYMOND.NS","WELSPUNIND.NS","GRASIM.NS",
    ],
    # ── Paints ───────────────────────────────────────────────────
    "Paints": [
        "ASIANPAINT.NS","BERGEPAINT.NS","KANSAINER.NS","AKZOINDIA.NS",
    ],
}

# Flat list + reverse sector map
ALL_STOCKS = []
STOCK_SECTOR_MAP = {}
for sector, tickers in FNO_STOCKS.items():
    for t in tickers:
        if t not in STOCK_SECTOR_MAP:   # avoid dups
            STOCK_SECTOR_MAP[t] = sector
            ALL_STOCKS.append(t)

# ─────────────────────────────────────────────────────────────────
#  SCANNER CORE
# ─────────────────────────────────────────────────────────────────
def ist_now():
    return datetime.now(IST)

def is_market_open():
    now = ist_now()
    if now.weekday() >= 5: return False
    return MARKET_OPEN <= (now.hour, now.minute) <= MARKET_CLOSE

def download_ohlcv(tickers, interval, start, end):
    data = {}
    for i in range(0, len(tickers), CONFIG["batch_size"]):
        batch = tickers[i:i+CONFIG["batch_size"]]
        try:
            raw = yf.download(batch, start=start, end=end, interval=interval,
                              auto_adjust=True, progress=False, threads=True)
            if raw.empty: continue
            def gc(name):
                if name in raw.columns:
                    s = raw[name]
                    return s.to_frame(name=batch[0]) if isinstance(s, pd.Series) else s
                try: return raw.xs(name, axis=1, level=0)
                except: return pd.DataFrame()
            cl, op, hi, lo, vo = gc("Close"), gc("Open"), gc("High"), gc("Low"), gc("Volume")
            for t in batch:
                if t not in cl.columns: continue
                c = cl[t].dropna()
                if len(c) < 5: continue
                data[t] = dict(close=c,
                               open=op[t].dropna()  if t in op.columns else pd.Series(),
                               high=hi[t].dropna()  if t in hi.columns else pd.Series(),
                               low=lo[t].dropna()   if t in lo.columns else pd.Series(),
                               volume=vo[t].dropna() if t in vo.columns else pd.Series())
        except: pass
        time.sleep(CONFIG["batch_pause_secs"])
    return data

def resample75(ohlcv):
    df = pd.DataFrame({k: ohlcv[k] for k in ("open","high","low","close","volume")})
    df.columns = ["Open","High","Low","Close","Volume"]
    df.index = pd.to_datetime(df.index)
    df = df.tz_localize("Asia/Kolkata") if df.index.tz is None else df.tz_convert("Asia/Kolkata")
    r = df.resample(f"{CONFIG['resample_minutes']}min", offset="9H15min").agg(
        {"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
    return {k.lower(): r[k] for k in r.columns}

def fetch_ath(tickers):
    start = (datetime.today()-timedelta(days=int(CONFIG["ath_lookback_years"]*365.25))).strftime("%Y-%m-%d")
    end   = (datetime.today()+timedelta(days=1)).strftime("%Y-%m-%d")
    raw   = download_ohlcv(tickers, "1d", start, end)
    return {t: float(v["high"].max()) for t, v in raw.items() if len(v["high"]) > 0}

def near_ath(price, ath):
    if not ath or np.isnan(ath) or ath <= 0: return False, None
    d = (ath - price) / ath * 100
    return CONFIG["ath_min_dist_pct"] <= d <= CONFIG["ath_max_dist_pct"], round(d, 2)

def consolidating(hi, lo, n, mx):
    if len(hi) < n: return False, None
    r = hi.iloc[-n:].max() - lo.iloc[-n:].min()
    p = r / lo.iloc[-n:].min() * 100
    return p <= mx, round(p, 2)

def avgvol(v, n=20):
    return float(v.iloc[-min(n,len(v)):].mean()) if len(v) >= 5 else 0

def ema(s, p): return s.ewm(span=p, adjust=False).mean()

# ─────────────────────────────────────────────────────────────────
#  GLOBAL STATE
# ─────────────────────────────────────────────────────────────────
state = dict(status="idle", last_scan=None, next_scan=None,
             sectors=[], stocks=[], scan_count=0, market_open=False, log=[])
_lock = threading.Lock()

def log(m):
    ts = ist_now().strftime("%H:%M:%S")
    line = f"[{ts}] {m}"
    with _lock:
        state["log"].append(line)
        if len(state["log"]) > 80: state["log"] = state["log"][-80:]
    print(line)

def run_scan():
    with _lock:
        state["status"] = "scanning"
        state["market_open"] = is_market_open()
        state["scan_count"] += 1
    log("▶ Scan started")
    try:
        # Sector ATH
        log("1/4 — Sector ATH (5-yr daily)…")
        idx = list(SECTOR_INDICES.values())
        ath_s = fetch_ath(idx)
        log("2/4 — Sector intraday…")
        start15 = (datetime.today()-timedelta(days=CONFIG["intraday_lookback_days"])).strftime("%Y-%m-%d")
        end15   = (datetime.today()+timedelta(days=1)).strftime("%Y-%m-%d")
        raw_s   = download_ohlcv(idx, "15m", start15, end15)
        sectors = []
        for sec, sym in SECTOR_INDICES.items():
            ath = ath_s.get(sym)
            if sym not in raw_s or not ath:
                sectors.append(dict(sector=sec,symbol=sym,ath=None,price=None,dist_pct=None,trending=False))
                continue
            try:
                c = resample75(raw_s[sym])
                price = float(c["close"].iloc[-1])
                q, d  = near_ath(price, ath)
                sectors.append(dict(sector=sec,symbol=sym,ath=round(ath,2),price=round(price,2),dist_pct=d,trending=q))
            except:
                sectors.append(dict(sector=sec,symbol=sym,ath=None,price=None,dist_pct=None,trending=False))
        # Sort ascending by dist (closest first), None last
        sectors.sort(key=lambda x: (x["dist_pct"] is None, x["dist_pct"] or 999))
        trending = {s["sector"] for s in sectors if s["trending"]}
        log(f"   Trending sectors: {', '.join(sorted(trending)) or 'none'}")

        # Stocks
        cands = [t for t in ALL_STOCKS if STOCK_SECTOR_MAP.get(t,"") in trending] or ALL_STOCKS
        log(f"3/4 — Stock ATH for {len(cands)} stocks…")
        ath_k = fetch_ath(cands)
        log(f"4/4 — Stock intraday scan…")
        raw_k = download_ohlcv(cands, "15m", start15, end15)
        stocks = []
        for t in cands:
            ath = ath_k.get(t)
            if t not in raw_k or not ath: continue
            try:
                c = resample75(raw_k[t])
                cl, hi, lo, vo = c["close"], c["high"], c["low"], c["volume"]
                if len(cl) < 10: continue
                av = avgvol(vo, 20)
                if av < CONFIG["min_avg_volume"]: continue
                pr = float(cl.iloc[-1])
                q, d = near_ath(pr, float(ath))
                if not q: continue
                ok, rng = consolidating(hi, lo, CONFIG["consol_candles"], CONFIG["max_range_pct"])
                if not ok: continue
                up = True
                if len(cl) >= CONFIG["ema_slow"]:
                    up = float(ema(cl, CONFIG["ema_fast"]).iloc[-1]) > float(ema(cl, CONFIG["ema_slow"]).iloc[-1])
                va = avgvol(vo, 10)
                vs = round(float(vo.iloc[-1])/va, 2) if va > 0 else 1.0
                ch = round((float(cl.iloc[-1])-float(cl.iloc[-6]))/float(cl.iloc[-6])*100,2) if len(cl)>=6 else 0.0
                stocks.append(dict(name=t.replace(".NS",""), sector=STOCK_SECTOR_MAP.get(t,""),
                                   price=round(pr,2), ath=round(float(ath),2), dist_pct=d,
                                   range_pct=rng, chg_1d=ch, vol_surge=vs, uptrend=up))
            except: pass
        stocks.sort(key=lambda x: x["dist_pct"])
        with _lock:
            state.update(sectors=sectors, stocks=stocks,
                         last_scan=ist_now().strftime("%d %b %Y, %H:%M:%S IST"),
                         next_scan=(ist_now()+timedelta(minutes=CONFIG["scan_interval_minutes"])).strftime("%H:%M IST"),
                         status="done")
        log(f"✅ Done — {len(stocks)} stocks qualified")
    except Exception as e:
        with _lock: state["status"] = "error"
        log(f"❌ Error: {e}")

def sched_loop():
    schedule.every(CONFIG["scan_interval_minutes"]).minutes.do(run_scan)
    while True:
        schedule.run_pending()
        time.sleep(30)

# ─────────────────────────────────────────────────────────────────
#  FLASK
# ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/api/data")
def api_data():
    with _lock: return jsonify(dict(state))

@app.route("/api/scan", methods=["POST"])
def api_scan():
    threading.Thread(target=run_scan, daemon=True).start()
    return jsonify({"ok": True})

@app.route("/")
def index(): return render_template_string(HTML)

# ─────────────────────────────────────────────────────────────────
#  DASHBOARD HTML  (bright professional theme)
# ─────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NSE F&O Scanner</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
:root {
  --bg:        #f0f4f8;
  --bg2:       #ffffff;
  --bg3:       #f7f9fb;
  --bg4:       #eef2f7;
  --border:    #d8e2ee;
  --border2:   #c2d0e0;
  --text:      #0f1923;
  --text2:     #3a4a5c;
  --muted:     #7a8fa8;
  --accent:    #0066ff;
  --accent-bg: #e8f0fe;
  --green:     #0a7c42;
  --green-bg:  #e6f4ed;
  --red:       #c0392b;
  --red-bg:    #fdecea;
  --orange:    #d4600a;
  --orange-bg: #fef0e6;
  --yellow:    #7a5a00;
  --yellow-bg: #fef9e6;
  --zone1:     #0a7c42;
  --zone2:     #1aab5e;
  --zone3:     #d4600a;
  --zone4:     #b03a00;
  --ff:  'Plus Jakarta Sans', sans-serif;
  --mono:'IBM Plex Mono', monospace;
  --r:   8px;
  --shadow: 0 1px 4px rgba(0,0,0,.07), 0 4px 16px rgba(0,0,0,.04);
  --shadow-md: 0 2px 8px rgba(0,0,0,.10), 0 8px 24px rgba(0,0,0,.06);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{font-family:var(--ff);background:var(--bg);color:var(--text);font-size:15px;line-height:1.5;}

/* ── TOPBAR ─────────────────────────────── */
.topbar{
  position:sticky;top:0;z-index:200;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;height:64px;
  background:#fff;border-bottom:2px solid var(--border);
  box-shadow:0 2px 12px rgba(0,0,0,.06);
}
.topbar-left{display:flex;align-items:center;gap:16px;}
.logo-mark{
  width:38px;height:38px;border-radius:9px;
  background:linear-gradient(135deg,#0044cc,#0066ff);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--ff);font-weight:800;font-size:14px;color:#fff;
  letter-spacing:-.02em;flex-shrink:0;
  box-shadow:0 2px 8px rgba(0,102,255,.3);
}
.logo-text{font-size:18px;font-weight:800;color:var(--text);letter-spacing:-.02em;}
.logo-sub{font-size:12px;color:var(--muted);font-weight:500;margin-top:1px;}
.topbar-right{display:flex;align-items:center;gap:20px;}
.market-badge{
  display:flex;align-items:center;gap:8px;
  padding:7px 14px;border-radius:20px;
  font-size:13px;font-weight:600;
  border:1.5px solid var(--border);
}
.market-badge.open{background:var(--green-bg);border-color:#a8dfc0;color:var(--green);}
.market-badge.closed{background:#f5f5f5;border-color:var(--border);color:var(--muted);}
.mdot{width:9px;height:9px;border-radius:50%;background:currentColor;flex-shrink:0;}
.market-badge.open .mdot{animation:pulse-g 2s infinite;}
@keyframes pulse-g{0%,100%{box-shadow:0 0 0 0 rgba(10,124,66,.5);}50%{box-shadow:0 0 0 5px rgba(10,124,66,0);}}
.scan-btn{
  display:flex;align-items:center;gap:8px;
  padding:9px 20px;border-radius:7px;
  background:linear-gradient(135deg,#0044cc,#0066ff);
  color:#fff;border:none;cursor:pointer;
  font-family:var(--ff);font-size:14px;font-weight:600;
  box-shadow:0 2px 8px rgba(0,102,255,.3);
  transition:all .2s;
}
.scan-btn:hover{background:linear-gradient(135deg,#003ab0,#0055dd);transform:translateY(-1px);box-shadow:0 4px 14px rgba(0,102,255,.4);}
.scan-btn:active{transform:translateY(0);}
.scan-btn:disabled{background:#c5ccd8;box-shadow:none;cursor:not-allowed;transform:none;}
.clock-chip{
  font-family:var(--mono);font-size:13px;font-weight:500;
  color:var(--text2);background:var(--bg4);
  padding:6px 12px;border-radius:6px;border:1px solid var(--border);
}

/* ── LAYOUT ─────────────────────────────── */
.content{max-width:1700px;margin:0 auto;padding:28px 32px 64px;}

/* ── STATUS BAR ─────────────────────────── */
.statusbar{
  display:flex;align-items:center;gap:0;
  background:#fff;border:1.5px solid var(--border);
  border-radius:var(--r);box-shadow:var(--shadow);
  margin-bottom:28px;overflow:hidden;
  flex-wrap:wrap;
}
.sb-item{
  display:flex;align-items:center;gap:10px;
  padding:14px 22px;font-size:14px;
  border-right:1px solid var(--border);
}
.sb-item:last-child{border-right:none;margin-left:auto;}
.sb-label{color:var(--muted);font-weight:500;}
.sb-val{color:var(--text);font-weight:700;}
.status-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:4px 12px;border-radius:20px;
  font-size:13px;font-weight:600;
}
.sp-idle    {background:#f0f0f0;color:var(--muted);}
.sp-scanning{background:var(--accent-bg);color:var(--accent);}
.sp-done    {background:var(--green-bg);color:var(--green);}
.sp-error   {background:var(--red-bg);color:var(--red);}
.spin{animation:spin .9s linear infinite;display:inline-block;}
@keyframes spin{to{transform:rotate(360deg);}}

/* ── SECTION HEADER ─────────────────────── */
.sec-head{display:flex;align-items:center;gap:14px;margin-bottom:18px;}
.sec-title{font-size:17px;font-weight:800;color:var(--text);letter-spacing:-.02em;}
.sec-sub{font-size:13px;color:var(--muted);font-weight:500;}
.sec-rule{flex:1;height:1.5px;background:var(--border);}
.sec-badge{
  padding:4px 12px;border-radius:20px;
  background:var(--accent-bg);color:var(--accent);
  font-size:12px;font-weight:700;
}

/* ── SECTOR GRID ─────────────────────────── */
.sector-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
  gap:14px;margin-bottom:36px;
}
.sc-card{
  background:#fff;border:1.5px solid var(--border);
  border-radius:var(--r);padding:18px 20px;
  box-shadow:var(--shadow);
  transition:all .2s;cursor:default;position:relative;overflow:hidden;
}
.sc-card:hover{box-shadow:var(--shadow-md);transform:translateY(-2px);}
.sc-card.trending{border-color:#a8dfc0;background:linear-gradient(145deg,#f0faf5,#fff);}
.sc-card.trending::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--green),#1aab5e);
}
.sc-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px;}
.sc-name{font-size:15px;font-weight:800;color:var(--text);}
.sc-sym{font-size:11px;color:var(--muted);margin-top:2px;font-family:var(--mono);}
.sc-badge2{
  padding:3px 9px;border-radius:5px;
  font-size:11px;font-weight:700;white-space:nowrap;
}
.sb-zone{background:var(--green-bg);color:var(--green);}
.sb-ath {background:var(--yellow-bg);color:var(--yellow);}
.sb-far {background:var(--bg4);color:var(--muted);}
.sb-na  {background:var(--bg4);color:var(--muted);}
.sc-dist-num{font-size:28px;font-weight:800;margin:4px 0 6px;font-family:var(--ff);letter-spacing:-.02em;}
.sc-meta{display:flex;justify-content:space-between;font-size:12.5px;color:var(--muted);margin-bottom:10px;}
.sc-meta span{font-weight:600;color:var(--text2);}

/* dist bar */
.dbar-wrap{margin-top:6px;}
.dbar-track{height:6px;background:var(--bg4);border-radius:3px;position:relative;overflow:visible;}
.dbar-zone{position:absolute;top:0;height:100%;background:rgba(10,124,66,.15);border-radius:3px;}
.dbar-fill{height:100%;border-radius:3px;position:absolute;top:0;left:0;transition:width .5s ease;}
.dbar-pin{
  width:12px;height:12px;border-radius:50%;
  position:absolute;top:-3px;transform:translateX(-50%);
  border:2.5px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.2);
  transition:left .5s ease;
}
.dbar-labels{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-top:3px;font-family:var(--mono);}

/* ── TABLE ────────────────────────────────── */
.table-card{
  background:#fff;border:1.5px solid var(--border);
  border-radius:var(--r);box-shadow:var(--shadow);
  overflow:hidden;margin-bottom:28px;
}
.table-toolbar{
  display:flex;align-items:center;gap:12px;
  padding:14px 20px;border-bottom:1.5px solid var(--border);
  background:var(--bg3);flex-wrap:wrap;
}
.tt-label{font-size:14px;font-weight:700;color:var(--text);}
.tt-count{font-size:13px;color:var(--muted);font-weight:500;}
.tt-search{
  margin-left:auto;
  padding:8px 14px;border-radius:6px;
  border:1.5px solid var(--border);
  font-family:var(--ff);font-size:14px;color:var(--text);
  background:#fff;outline:none;width:220px;
}
.tt-search:focus{border-color:var(--accent);}
.tbl-wrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;}
thead th{
  padding:13px 16px;
  background:var(--bg3);
  border-bottom:2px solid var(--border);
  font-size:13px;font-weight:700;color:var(--text2);
  text-align:left;white-space:nowrap;
  cursor:pointer;user-select:none;
  position:sticky;top:0;
}
thead th:hover{background:var(--bg4);color:var(--accent);}
thead th.right{text-align:right;}
thead th .sort-icon{margin-left:6px;font-size:11px;opacity:.4;}
thead th.sort-asc .sort-icon::after{content:'↑';opacity:1;color:var(--accent);}
thead th.sort-desc .sort-icon::after{content:'↓';opacity:1;color:var(--accent);}
thead th:not(.sort-asc):not(.sort-desc) .sort-icon::after{content:'↕';}
tbody tr{border-bottom:1px solid var(--border);transition:background .12s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:#f5f8ff;}
tbody td{padding:12px 16px;font-size:14px;vertical-align:middle;white-space:nowrap;}
tbody td.right{text-align:right;}

.td-rank{
  font-family:var(--mono);font-size:12px;font-weight:600;
  color:var(--muted);width:32px;
}
.td-name{font-size:15px;font-weight:800;color:var(--text);}
.td-sector{font-size:12px;color:var(--muted);font-weight:500;margin-top:2px;}
.td-price{font-size:15px;font-weight:700;color:var(--text);font-family:var(--mono);}
.td-ath{font-size:12px;color:var(--muted);font-family:var(--mono);}
.dist-pill{
  display:inline-flex;align-items:center;
  padding:5px 12px;border-radius:20px;
  font-size:13px;font-weight:700;font-family:var(--mono);
}
.dp-z1{background:var(--green-bg);color:var(--zone1);}
.dp-z2{background:#d4f4e2;color:var(--zone2);}
.dp-z3{background:var(--orange-bg);color:var(--zone3);}
.dp-z4{background:#fde8d8;color:var(--zone4);}
.range-pill{
  display:inline-block;padding:4px 10px;border-radius:5px;
  background:#eef2ff;color:#3355cc;
  font-size:13px;font-weight:600;font-family:var(--mono);
}
.chg-pos{color:var(--green);font-weight:700;font-family:var(--mono);}
.chg-neg{color:var(--red);font-weight:700;font-family:var(--mono);}
.vs-high{color:var(--green);font-weight:700;font-family:var(--mono);}
.vs-norm{color:var(--muted);font-family:var(--mono);}
.trend-up{
  display:inline-flex;align-items:center;justify-content:center;
  width:28px;height:28px;border-radius:6px;
  background:var(--green-bg);color:var(--green);font-size:14px;font-weight:700;
}
.trend-down{
  display:inline-flex;align-items:center;justify-content:center;
  width:28px;height:28px;border-radius:6px;
  background:var(--yellow-bg);color:var(--orange);font-size:14px;
}

/* ── LEGEND ──────────────────────────────── */
.legend{
  display:flex;align-items:center;gap:20px;flex-wrap:wrap;
  margin-bottom:16px;padding:12px 16px;
  background:#fff;border:1.5px solid var(--border);
  border-radius:var(--r);box-shadow:var(--shadow);
  font-size:13px;
}
.leg-item{display:flex;align-items:center;gap:7px;font-weight:500;color:var(--text2);}
.leg-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0;}
.leg-sep{width:1px;height:18px;background:var(--border);}

/* ── LOG ─────────────────────────────────── */
.log-card{
  background:#fff;border:1.5px solid var(--border);
  border-radius:var(--r);box-shadow:var(--shadow);overflow:hidden;
}
.log-head{
  display:flex;align-items:center;gap:10px;
  padding:12px 20px;background:var(--bg3);
  border-bottom:1.5px solid var(--border);
  font-size:14px;font-weight:700;color:var(--text2);
}
.log-body{max-height:180px;overflow-y:auto;padding:12px 20px;font-family:var(--mono);font-size:13px;line-height:1.7;}
.ll-ok  {color:var(--green);}
.ll-warn{color:var(--orange);}
.ll-err {color:var(--red);}
.ll-def {color:var(--muted);}

/* ── EMPTY STATE ─────────────────────────── */
.empty{text-align:center;padding:60px 20px;color:var(--muted);}
.empty .eico{font-size:40px;margin-bottom:16px;}
.empty .etxt{font-size:16px;font-weight:600;color:var(--text2);}
.empty .esub{font-size:14px;margin-top:6px;}

/* ── SCROLLBAR ───────────────────────────── */
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg4);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}

@media(max-width:768px){
  .content{padding:16px;}
  .topbar{padding:0 16px;}
  .sector-grid{grid-template-columns:1fr 1fr;}
  .tt-search{width:140px;}
  .sb-item:nth-child(n+3){display:none;}
}
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-mark">NSE</div>
    <div>
      <div class="logo-text">F&amp;O Consolidation Scanner</div>
      <div class="logo-sub">220 Stocks · 75-Min Candles · 0–15% ATH Band · Auto-scan every 15 min</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="clock-chip" id="clock">--:--:-- IST</div>
    <div class="market-badge" id="mktBadge">
      <div class="mdot"></div>
      <span id="mktTxt">MARKET</span>
    </div>
    <button class="scan-btn" id="scanBtn" onclick="triggerScan()">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M13.5 8A5.5 5.5 0 1 1 8 2.5"/>
        <path d="M13.5 2.5v3h-3"/>
      </svg>
      Scan Now
    </button>
  </div>
</div>

<div class="content">

  <!-- STATUS BAR -->
  <div class="statusbar">
    <div class="sb-item"><span class="sb-label">Status</span><span id="statusPill"><span class="status-pill sp-idle">Idle</span></span></div>
    <div class="sb-item"><span class="sb-label">Last Scan</span><span class="sb-val" id="lastScan">—</span></div>
    <div class="sb-item"><span class="sb-label">Next Scan</span><span class="sb-val" id="nextScan">—</span></div>
    <div class="sb-item"><span class="sb-label">Universe</span><span class="sb-val">220 F&amp;O Stocks</span></div>
    <div class="sb-item"><span class="sb-label">Scan #</span><span class="sb-val" id="scanCount">0</span></div>
  </div>

  <!-- SECTORS -->
  <div class="sec-head">
    <div class="sec-title">Sector Heatmap</div>
    <div id="secBadge" class="sec-badge">— trending</div>
    <div class="sec-sub">Sorted by % from ATH ↑</div>
    <div class="sec-rule"></div>
  </div>

  <div class="legend">
    <div class="leg-item"><div class="leg-dot" style="background:#0a7c42"></div>0–7% from ATH — Very Near</div>
    <div class="leg-sep"></div>
    <div class="leg-item"><div class="leg-dot" style="background:#1aab5e"></div>7–10%</div>
    <div class="leg-sep"></div>
    <div class="leg-item"><div class="leg-dot" style="background:#d4600a"></div>10–13%</div>
    <div class="leg-sep"></div>
    <div class="leg-item"><div class="leg-dot" style="background:#b03a00"></div>13–15% — Far Edge</div>
    <div class="leg-sep"></div>
    <div class="leg-item" style="margin-left:auto;color:var(--muted);font-size:12px;">
      ✅ Green border = in 0–15% ATH zone
    </div>
  </div>

  <div class="sector-grid" id="sectorGrid">
    <div class="empty" style="grid-column:1/-1">
      <div class="eico">📡</div>
      <div class="etxt">Awaiting first scan</div>
      <div class="esub">Click <b>Scan Now</b> to begin</div>
    </div>
  </div>

  <!-- STOCKS TABLE -->
  <div class="sec-head">
    <div class="sec-title">Qualified Stocks</div>
    <div id="stockBadge" class="sec-badge">0 results</div>
    <div class="sec-sub">Consolidating 0–15% below ATH in trending sectors</div>
    <div class="sec-rule"></div>
  </div>

  <div class="table-card">
    <div class="table-toolbar">
      <div class="tt-label">Results</div>
      <div class="tt-count" id="tblCount">—</div>
      <input class="tt-search" id="searchBox" type="text" placeholder="Search stock or sector…" oninput="filterTable()"/>
    </div>
    <div class="tbl-wrap">
      <table id="stockTable">
        <thead>
          <tr>
            <th data-col="idx">#<span class="sort-icon"></span></th>
            <th data-col="name">Stock<span class="sort-icon"></span></th>
            <th data-col="sector">Sector<span class="sort-icon"></span></th>
            <th data-col="price" class="right">CMP ₹<span class="sort-icon"></span></th>
            <th data-col="ath" class="right">ATH ₹<span class="sort-icon"></span></th>
            <th data-col="dist_pct" class="right sort-asc">Dist ATH ↑<span class="sort-icon"></span></th>
            <th data-col="range_pct" class="right">8C Range<span class="sort-icon"></span></th>
            <th data-col="chg_1d" class="right">1D Chg%<span class="sort-icon"></span></th>
            <th data-col="vol_surge" class="right">Vol Surge<span class="sort-icon"></span></th>
            <th data-col="uptrend" class="right">Trend<span class="sort-icon"></span></th>
          </tr>
        </thead>
        <tbody id="stockTbody">
          <tr><td colspan="10">
            <div class="empty">
              <div class="eico">🔍</div>
              <div class="etxt">No results yet</div>
              <div class="esub">Trigger a scan to populate</div>
            </div>
          </td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- LOG -->
  <div class="log-card">
    <div class="log-head">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H2zm0 1h12v12H2V2zm2 2v2h8V4H4zm0 4v2h8V8H4zm0 4v2h5v-2H4z"/></svg>
      Scan Activity Log
    </div>
    <div class="log-body" id="logBody"><div class="ll-def">Waiting for scan…</div></div>
  </div>

</div>

<script>
// ── DATA ──────────────────────────────────────────────────────
let allStocks  = [];
let sortCol    = 'dist_pct';
let sortDir    = 'asc';   // ascending = closest to ATH first

function distClass(d){
  if(d===null||d===undefined) return '';
  if(d<=7)  return 'dp-z1';
  if(d<=10) return 'dp-z2';
  if(d<=13) return 'dp-z3';
  return 'dp-z4';
}
function distColor(d){
  const m={dp_z1:'#0a7c42',dp_z2:'#1aab5e',dp_z3:'#d4600a',dp_z4:'#b03a00'};
  return m[distClass(d).replace(/-/g,'_')]||'#7a8fa8';
}
function fmt(n,d=2){return n===null||n===undefined?'—':Number(n).toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});}

// ── SECTORS ──────────────────────────────────────────────────
function renderSectors(sectors){
  const g = document.getElementById('sectorGrid');
  const t = sectors.filter(s=>s.trending).length;
  document.getElementById('secBadge').textContent = `${t} trending`;

  if(!sectors.length){
    g.innerHTML=`<div class="empty" style="grid-column:1/-1">
      <div class="eico">📉</div><div class="etxt">No sector data</div></div>`;
    return;
  }

  g.innerHTML = sectors.map(s=>{
    const d   = s.dist_pct;
    const col = distColor(d);
    const pct = d!==null ? d.toFixed(1) : '—';
    let badgeCls='sb-na', badgeTxt='N/A';
    if(s.ath && d!==null){
      if(s.trending){badgeCls='sb-zone';badgeTxt='In Zone';}
      else if(d<5)   {badgeCls='sb-ath'; badgeTxt='At ATH';}
      else           {badgeCls='sb-far'; badgeTxt='Too Far';}
    }
    const barW     = d!==null ? Math.min(d/15*100,100) : 0;
    const zL       = 5/15*100;
    const zW       = 10/15*100;
    const ath_s    = s.ath  ? '₹'+Number(s.ath).toLocaleString('en-IN')  : '—';
    const price_s  = s.price? '₹'+Number(s.price).toLocaleString('en-IN') : '—';

    return `<div class="sc-card ${s.trending?'trending':''}">
      <div class="sc-top">
        <div><div class="sc-name">${s.sector}</div><div class="sc-sym">${s.symbol}</div></div>
        <span class="sc-badge2 ${badgeCls}">${badgeTxt}</span>
      </div>
      <div class="sc-dist-num" style="color:${col}">${pct}%</div>
      <div class="sc-meta">
        <div>ATH <span>${ath_s}</span></div>
        <div>Now <span>${price_s}</span></div>
      </div>
      <div class="dbar-wrap">
        <div class="dbar-track">
          <div class="dbar-zone" style="left:${zL}%;width:${zW}%"></div>
          <div class="dbar-fill" style="width:${barW}%;background:${col}22"></div>
          <div class="dbar-pin"  style="left:${barW}%;background:${col}"></div>
        </div>
        <div class="dbar-labels"><span>0%</span><span>5%</span><span>10%</span><span>15%</span></div>
      </div>
    </div>`;
  }).join('');
}

// ── TABLE ─────────────────────────────────────────────────────
function sortData(data){
  return [...data].sort((a,b)=>{
    let av=a[sortCol], bv=b[sortCol];
    if(sortCol==='name'||sortCol==='sector'){
      av=(av||'').toLowerCase(); bv=(bv||'').toLowerCase();
      return sortDir==='asc'?(av<bv?-1:av>bv?1:0):(av>bv?-1:av<bv?1:0);
    }
    if(sortCol==='uptrend'){av=av?1:0;bv=bv?1:0;}
    av=av??99999; bv=bv??99999;
    return sortDir==='asc'?av-bv:bv-av;
  });
}

function filterTable(){
  const q = document.getElementById('searchBox').value.trim().toLowerCase();
  const filtered = q ? allStocks.filter(s=>
    s.name.toLowerCase().includes(q)||s.sector.toLowerCase().includes(q)
  ) : allStocks;
  renderRows(sortData(filtered));
}

function renderRows(data){
  const tbody = document.getElementById('stockTbody');
  document.getElementById('tblCount').textContent =
    `${data.length} result${data.length!==1?'s':''}`;
  document.getElementById('stockBadge').textContent =
    `${allStocks.length} results`;

  if(!data.length){
    tbody.innerHTML=`<tr><td colspan="10"><div class="empty">
      <div class="eico">🔍</div>
      <div class="etxt">No stocks matched criteria</div>
      <div class="esub">All sectors may be outside the 0–15% ATH band</div>
    </div></td></tr>`;
    return;
  }

  tbody.innerHTML = data.map((s,i)=>{
    const dc  = distClass(s.dist_pct);
    const chgC= s.chg_1d>=0?'chg-pos':'chg-neg';
    const chgS= (s.chg_1d>=0?'+':'')+fmt(s.chg_1d)+'%';
    const vsC = s.vol_surge>=1.5?'vs-high':'vs-norm';
    const tIco= s.uptrend
      ? `<span class="trend-up">▲</span>`
      : `<span class="trend-down">~</span>`;
    return `<tr>
      <td><span class="td-rank">${i+1}</span></td>
      <td><div class="td-name">${s.name}</div><div class="td-sector">${s.sector}</div></td>
      <td><span style="font-size:13px;font-weight:600;color:var(--text2)">${s.sector}</span></td>
      <td class="right"><div class="td-price">${fmt(s.price)}</div></td>
      <td class="right"><div class="td-ath">${fmt(s.ath)}</div></td>
      <td class="right"><span class="dist-pill ${dc}" data-val="${s.dist_pct}">${fmt(s.dist_pct,1)}%</span></td>
      <td class="right"><span class="range-pill">${fmt(s.range_pct,1)}%</span></td>
      <td class="right"><span class="${chgC}">${chgS}</span></td>
      <td class="right"><span class="${vsC}">${fmt(s.vol_surge,2)}x</span></td>
      <td class="right">${tIco}</td>
    </tr>`;
  }).join('');
}

// ── SORT HEADERS ─────────────────────────────────────────────
document.querySelectorAll('thead th[data-col]').forEach(th=>{
  th.addEventListener('click',()=>{
    const col = th.dataset.col;
    if(sortCol===col) sortDir = sortDir==='asc'?'desc':'asc';
    else { sortCol=col; sortDir='asc'; }
    document.querySelectorAll('thead th').forEach(h=>{
      h.classList.remove('sort-asc','sort-desc');
    });
    th.classList.add(sortDir==='asc'?'sort-asc':'sort-desc');
    filterTable();
  });
});

// ── STATUS ────────────────────────────────────────────────────
function renderStatus(d){
  const map={
    idle:    ['Idle',      'sp-idle'],
    scanning:['Scanning…', 'sp-scanning'],
    done:    ['Done',      'sp-done'],
    error:   ['Error',     'sp-error'],
  };
  const [lbl,cls]=map[d.status]||['—','sp-idle'];
  const spin=d.status==='scanning'?'<span class="spin"> ⟳</span>':'';
  document.getElementById('statusPill').innerHTML=
    `<span class="status-pill ${cls}">${lbl}${spin}</span>`;
  document.getElementById('lastScan').textContent  = d.last_scan||'—';
  document.getElementById('nextScan').textContent  = d.next_scan||'—';
  document.getElementById('scanCount').textContent = d.scan_count||0;

  const badge=document.getElementById('mktBadge');
  const txt=document.getElementById('mktTxt');
  if(d.market_open){badge.className='market-badge open';txt.textContent='NSE OPEN';}
  else             {badge.className='market-badge closed';txt.textContent='NSE CLOSED';}
  document.getElementById('scanBtn').disabled = d.status==='scanning';
}

// ── LOG ───────────────────────────────────────────────────────
function renderLog(lines){
  if(!lines||!lines.length) return;
  document.getElementById('logBody').innerHTML =
    [...lines].reverse().map(l=>{
      let c='ll-def';
      if(l.includes('✅')||l.includes('Done')) c='ll-ok';
      else if(l.includes('⚠')||l.includes('warn')) c='ll-warn';
      else if(l.includes('❌')||l.includes('Error')) c='ll-err';
      return `<div class="${c}">${l}</div>`;
    }).join('');
}

// ── POLL ─────────────────────────────────────────────────────
async function fetchData(){
  try{
    const r=await fetch('/api/data');
    const d=await r.json();
    renderStatus(d);
    renderSectors(d.sectors||[]);
    allStocks = d.stocks||[];
    filterTable();
    renderLog(d.log||[]);
  }catch(e){console.error(e);}
}

async function triggerScan(){
  await fetch('/api/scan',{method:'POST'});
  setTimeout(fetchData,500);
}

// ── CLOCK ─────────────────────────────────────────────────────
function updateClock(){
  const el=document.getElementById('clock');
  const ist=new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Kolkata'}));
  el.textContent=ist.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'})+' IST';
}

setInterval(fetchData,  5000);
setInterval(updateClock,1000);
fetchData();
updateClock();
</script>
</body>
</html>"""

if __name__ == "__main__":
    print("="*60)
    print("  NSE F&O CONSOLIDATION SCANNER  — DASHBOARD v2")
    print("  Universe : 220 F&O Stocks")
    print("  Open     : http://localhost:5050")
    print("="*60)
    threading.Thread(target=run_scan,   daemon=True).start()
    threading.Thread(target=sched_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
