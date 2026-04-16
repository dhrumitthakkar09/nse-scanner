# NSE F&O Consolidation Scanner — Dashboard v2

A web dashboard that scans 220 NSE F&O stocks every 15 minutes, identifies stocks
consolidating near their all-time highs, and sends Telegram alerts for new signals.

- **Data source**: Dhan HQ API (15-min intraday + daily historical)
- **Candle timeframe**: 75-min (resampled from 15-min)
- **Scan criteria**: Within 0–15% of 5-year ATH · Consolidating ≤5% range over 8 candles · Avg volume ≥ 200K · EMA(9) > EMA(21)
- **Alerts**: Telegram message when new stocks enter the qualified list

---

## Project structure

```
nse_dashboard_v2/
├── config/
│   ├── settings.py       # CONFIG dict, CREDENTIALS, YAML helpers
│   ├── stocks.py         # 220 F&O stock universe by sector
│   └── sectors.py        # Sector → Nifty index name mapping
├── data/
│   ├── dhan_api.py       # Raw Dhan API HTTP wrappers
│   ├── fetcher.py        # Batch fetch helpers (OHLCV, ATH)
│   └── scrip_master.py   # Dhan scrip master CSV → security_id lookup
├── scanner/
│   ├── core.py           # Pure scan functions (resample, ATH check, consolidation)
│   ├── alerts.py         # Telegram alert sender
│   └── runner.py         # Scan orchestrator, shared state, scheduler
├── web/
│   ├── routes.py         # Flask app and all API routes
│   └── template.py       # Dashboard HTML/CSS/JS
├── nse_dashboard_v2.py   # Entry point
└── requirements.txt
```

---

## Prerequisites

- Python 3.11 or higher
- A [Dhan HQ](https://dhanhq.co) account with API access enabled
- (Optional) A Telegram bot for alerts

---

## Setup

### 1. Clone or download the project

```bash
git clone <repo-url>
cd nse_dashboard_v2
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the config file

Create a file at `../dhan/config.yaml` (one level above this project) with your credentials:

```yaml
dhan:
  client_id: "YOUR_CLIENT_ID"
  access_token: "YOUR_ACCESS_TOKEN"

telegram:
  bot_token: "YOUR_BOT_TOKEN"      # optional
  chat_id: "YOUR_CHAT_ID"          # optional
```

**Getting Dhan credentials:**
1. Log in to [Dhan HQ](https://dhanhq.co)
2. Go to My Profile → API Access
3. Copy your Client ID and generate an Access Token

**Getting Telegram credentials (optional):**
1. Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot`
2. Copy the bot token it gives you
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

> You can also set credentials later through the Settings tab in the dashboard.

---

## Running

```bash
python nse_dashboard_v2.py
```

Then open your browser at:

```
http://localhost:5050
```

The scanner will:
1. Download the Dhan scrip master on startup (one-time, ~5 seconds)
2. Run an initial scan immediately
3. Re-scan automatically every 15 minutes

---

## Dashboard tabs

| Tab | What it shows |
|---|---|
| **Scanner** | Qualified stocks table with price, ATH distance, range %, volume surge, trend |
| **Sectors** | Heatmap of sector ATH proximity + gainers/losers |
| **Settings** | Configure Dhan credentials, Telegram, and scan parameters |

---

## Configuring scan parameters

All parameters can be changed live from the **Settings** tab without restarting:

| Parameter | Default | Description |
|---|---|---|
| Scan interval | 15 min | How often the scanner runs |
| ATH max distance | 15% | Only show stocks within this % of their 5Y ATH |
| Consolidation candles | 8 | Number of 75-min candles to check for tight range |
| Max range % | 5% | Max high-low range over consolidation candles |
| Min avg volume | 200,000 | Minimum 20-candle average volume |
| API delay | 0.4 sec | Delay between Dhan API calls (rate limiting) |

---

## Troubleshooting

**Dashboard shows "Awaiting first scan" indefinitely**
- Check that your Dhan credentials are set correctly in Settings or `config.yaml`
- The scrip master download requires internet access on startup

**Telegram alerts not sending**
- Use the "Test Alert" button in Settings to verify the connection
- Make sure the bot has been started by messaging it `/start`
- For group/channel IDs, the bot must be a member of the group

**`ModuleNotFoundError` on startup**
- Make sure you activated your virtual environment before running
- Re-run `pip install -r requirements.txt`
