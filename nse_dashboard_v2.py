"""
NSE F&O Consolidation Scanner — Dashboard v2
============================================
Entry point.  All logic lives in sub-packages:

  config/    — settings, stock universe, sector indices
  data/      — Dhan API wrappers, fetcher helpers, scrip master
  scanner/   — pure scan logic (core), alerts, scan runner
  web/       — Flask routes, HTML template

Run:
    python nse_dashboard_v2.py

Open:
    http://localhost:5050
"""

import threading
import warnings

warnings.filterwarnings("ignore")

from config.settings import CREDENTIALS
from data import scrip_master
from scanner import alerts
from scanner.runner import run_scan, sched_loop
from web.routes import app

if __name__ == "__main__":
    print("=" * 60)
    print("  NSE F&O CONSOLIDATION SCANNER  — DASHBOARD v2")
    print(f"  Data     : Dhan API  (client: {CREDENTIALS.get('dhan_client_id') or '⚠ NOT SET'})")
    print(f"  Telegram : {'configured' if alerts.is_configured() else '⚠ NOT configured (set in config.yaml)'}")
    print("  Universe : 220 F&O Stocks")
    print("  Open     : http://localhost:5050")
    print("=" * 60)

    threading.Thread(target=scrip_master.load, daemon=True).start()
    threading.Thread(target=run_scan,          daemon=True).start()
    threading.Thread(target=sched_loop,        daemon=True).start()

    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
