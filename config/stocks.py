"""
NSE F&O stock universe — Dhan trading symbols (no .NS suffix).

Provides:
  FNO_STOCKS       — sector → [symbols] dict
  ALL_STOCKS       — flat deduplicated list
  STOCK_SECTOR_MAP — symbol → sector reverse lookup
"""

FNO_STOCKS: dict[str, list[str]] = {
    # ── IT / Technology ──────────────────────────────────────────
    "IT": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM",
        "LTIM", "MPHASIS", "COFORGE", "PERSISTENT", "TATAELXSI",
        "OFSS", "KPITTECH", "ZENSAR", "RATEGAIN", "ZOMATO",
        "NAUKRI", "INDIAMART", "MAPMYINDIA",
    ],
    # ── Banking ───────────────────────────────────────────────────
    "Bank": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK",
        "INDUSINDBK", "BANKBARODA", "FEDERALBNK", "IDFCFIRSTB",
        "RBLBANK", "BANDHANBNK", "KARURVYSYA", "DCBBANK",
        "CSBBANK", "UJJIVANSFB",
    ],
    # ── PSU Bank ─────────────────────────────────────────────────
    "PSU Bank": [
        "CANBK", "PNB", "UNIONBANK", "MAHABANK", "CENTRALBK",
        "IOB", "INDIANB", "J&KBANK",
    ],
    # ── Financial Services ───────────────────────────────────────
    "Financial Svcs": [
        "BAJFINANCE", "BAJAJFINSV", "CHOLAFIN", "SBICARD",
        "SHRIRAMFIN", "HDFCLIFE", "SBILIFE", "ICICIGI",
        "ICICIPRULI", "RECLTD", "IRFC", "POLICYBZR",
        "MUTHOOTFIN", "MANAPPURAM", "LICHSGFIN", "PNBHOUSING",
        "ABCAPITAL", "M&MFIN", "SUNDARMFIN",
        "CANFINHOME", "HOMEFIRST", "CREDITACC",
    ],
    # ── Auto ─────────────────────────────────────────────────────
    "Auto": [
        "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT",
        "HEROMOTOCO", "MOTHERSON", "BOSCHLTD", "BHARATFORG",
        "BALKRISIND", "APOLLOTYRE", "CEATLTD", "MRF", "TIINDIA",
        "ENDURANCE", "TVSMOTOR", "ASHOKLEY",
    ],
    # ── Pharma / Healthcare ──────────────────────────────────────
    "Pharma": [
        "SUNPHARMA", "DIVISLAB", "DRREDDY", "CIPLA", "AUROPHARMA",
        "LUPIN", "TORNTPHARM", "APOLLOHOSP", "ALKEM", "BIOCON",
        "GLENMARK", "IPCALAB", "NATCOPHARM", "GRANULES", "LAURUSLABS",
        "ABBOTINDIA", "FORTIS", "METROPOLIS", "MAXHEALTH",
    ],
    # ── FMCG / Consumer ──────────────────────────────────────────
    "FMCG": [
        "HINDUNILVR", "ITC", "NESTLEIND", "TITAN", "BRITANNIA",
        "TATACONSUM", "MARICO", "GODREJCP", "COLPAL", "PGHH",
        "UBL", "MCDOWELL-N", "ASIANPAINT", "BERGEPAINT", "PIDILITIND",
        "DABUR", "EMAMILTD", "VBL", "ZYDUSLIFE", "RADICO",
    ],
    # ── Metal / Mining ───────────────────────────────────────────
    "Metal": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA",
        "SRF", "SAIL", "NMDC", "NATIONALUM", "HINDCOPPER",
        "RATNAMANI", "APLAPOLLO", "MOIL",
    ],
    # ── Energy / Oil & Gas ───────────────────────────────────────
    "Energy": [
        "RELIANCE", "ONGC", "NTPC", "POWERGRID", "BPCL",
        "GAIL", "TATAPOWER", "ADANIGREEN", "NHPC",
        "ADANIENT", "IOC", "HINDPETRO", "PETRONET", "GUJGASLTD",
        "IGL", "MGL", "CESC", "TORNTPOWER", "JSPL",
    ],
    # ── Realty ───────────────────────────────────────────────────
    "Realty": [
        "DLF", "LODHA", "GODREJPROP", "OBEROIRLTY", "PRESTIGE",
        "BRIGADE", "SOBHA", "PHOENIXLTD", "SUNTECK",
    ],
    # ── Infra / Capital Goods ────────────────────────────────────
    "Infra": [
        "LT", "ABB", "SIEMENS", "BEL", "ADANIPORTS",
        "INDUSTOWER", "IRCTC", "HAVELLS", "VOLTAS", "ULTRACEMCO",
        "AMBUJACEM", "GRASIM", "BHARTIARTL",
        "CUMMINSIND", "THERMAX", "BHEL", "IRCON", "RVNL",
        "NBCC", "PFC", "HUDCO",
    ],
    # ── Media / Telecom ──────────────────────────────────────────
    "Media": [
        "ZEEL", "SUNTV", "PVRINOX", "NETWORK18", "TV18BRDCST",
    ],
    # ── Chemicals ────────────────────────────────────────────────
    "Chemicals": [
        "PIDILITIND", "DEEPAKNTR", "AARTIIND", "NAVINFLUOR",
        "TATACHEM", "GSFC", "GNFC",
        "CHAMBLFERT", "COROMANDEL", "PIIND", "RALLIS",
    ],
    # ── Paints ───────────────────────────────────────────────────
    "Paints": [
        "ASIANPAINT", "BERGEPAINT", "KANSAINER", "AKZOINDIA",
    ],
}

# ── Derived flat structures ───────────────────────────────────
ALL_STOCKS: list[str] = []
STOCK_SECTOR_MAP: dict[str, str] = {}

for _sector, _tickers in FNO_STOCKS.items():
    for _t in _tickers:
        if _t not in STOCK_SECTOR_MAP:
            STOCK_SECTOR_MAP[_t] = _sector
            ALL_STOCKS.append(_t)
