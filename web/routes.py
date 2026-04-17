"""
Flask application and all HTTP routes.

Imports shared state from scanner.runner (read-only via _lock) and
config helpers from config.settings to serve and persist settings.
"""

import threading

from flask import Flask, jsonify, render_template_string, request

from config.settings import CONFIG, CREDENTIALS, load_yaml, save_yaml
from data import scrip_master
from scanner import alerts
from scanner.runner import _lock, run_scan, state
from web.template import HTML

app = Flask(__name__)


# ── Data / scan ───────────────────────────────────────────────────

@app.route("/api/data")
def api_data():
    with _lock:
        return jsonify(dict(state))


@app.route("/api/scan", methods=["POST"])
def api_scan():
    threading.Thread(target=run_scan, daemon=True).start()
    return jsonify({"ok": True})


# ── Settings ──────────────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    cfg = load_yaml()
    return jsonify({
        "dhan_client_id":        cfg.get("dhan", {}).get("client_id", ""),
        "dhan_access_token":     cfg.get("dhan", {}).get("access_token", ""),
        "telegram_bot_token":    cfg.get("telegram", {}).get("bot_token", ""),
        "telegram_chat_id":      cfg.get("telegram", {}).get("chat_id", ""),
        "scan_interval_minutes": CONFIG["scan_interval_minutes"],
        "ath_max_dist_pct":      CONFIG["ath_max_dist_pct"],
        "max_range_pct":         CONFIG["max_range_pct"],
        "consol_candles":        CONFIG["consol_candles"],
        "min_avg_volume":        CONFIG["min_avg_volume"],
        "api_call_delay_secs":   CONFIG["api_call_delay_secs"],
    })


@app.route("/api/settings", methods=["POST"])
def api_settings_post():
    data = request.get_json() or {}
    cfg  = load_yaml() or {}
    cfg.setdefault("dhan", {})
    cfg.setdefault("telegram", {})

    # Credentials — update in-memory dict and persist to YAML
    if data.get("dhan_client_id"):
        cfg["dhan"]["client_id"]        = data["dhan_client_id"]
        CREDENTIALS["dhan_client_id"]   = data["dhan_client_id"]
    if data.get("dhan_access_token"):
        cfg["dhan"]["access_token"]       = data["dhan_access_token"]
        CREDENTIALS["dhan_access_token"]  = data["dhan_access_token"]
    if "telegram_bot_token" in data:
        cfg["telegram"]["bot_token"]          = data["telegram_bot_token"]
        CREDENTIALS["telegram_bot_token"]     = data["telegram_bot_token"]
    if "telegram_chat_id" in data:
        cfg["telegram"]["chat_id"]            = data["telegram_chat_id"]
        CREDENTIALS["telegram_chat_id"]       = data["telegram_chat_id"]

    # Scanner parameters — update in-memory CONFIG dict
    for key in ("scan_interval_minutes", "consol_candles"):
        if key in data:
            try:
                CONFIG[key] = int(data[key])
            except (ValueError, TypeError):
                pass
    for key in ("ath_max_dist_pct", "max_range_pct", "api_call_delay_secs"):
        if key in data:
            try:
                CONFIG[key] = float(data[key])
            except (ValueError, TypeError):
                pass
    if "min_avg_volume" in data:
        try:
            CONFIG["min_avg_volume"] = int(data["min_avg_volume"])
        except (ValueError, TypeError):
            pass

    save_yaml(cfg)
    return jsonify({"ok": True, "message": "Settings saved"})


# ── Scrip master ─────────────────────────────────────────────────

@app.route("/api/scrip-debug")
def api_scrip_debug():
    """Diagnostic endpoint — shows scrip master stats, column values, and per-stock lookup."""
    from config.stocks import ALL_STOCKS
    from scanner.runner import _eq_sid
    eq_keys   = list(scrip_master.EQUITY_MAP.keys())
    idx_keys  = list(scrip_master.INDEX_MAP.keys())
    hits      = [s for s in ALL_STOCKS if _eq_sid(s) is not None]
    misses    = [s for s in ALL_STOCKS if _eq_sid(s) is None]
    return jsonify({
        "equity_map_size":    len(eq_keys),
        "index_map_size":     len(idx_keys),
        "sample_equity_keys": eq_keys[:10],
        "sample_index_keys":  idx_keys[:10],
        "stocks_with_id":     len(hits),
        "stocks_missing_id":  len(misses),
        "missing_samples":    misses[:20],
        "load_info":          scrip_master.load_info,
    })


@app.route("/api/reload-scrip", methods=["POST"])
def api_reload_scrip():
    """Force re-download and re-parse the Dhan scrip master CSV."""
    try:
        scrip_master.force_reload()
        from config.stocks import ALL_STOCKS
        from scanner.runner import _eq_sid
        hits = sum(1 for s in ALL_STOCKS if _eq_sid(s) is not None)
        return jsonify({"ok": True, "stocks_with_id": hits, "total": len(ALL_STOCKS)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)})


# ── Telegram test ─────────────────────────────────────────────────

@app.route("/api/test-telegram", methods=["POST"])
def api_test_telegram():
    ok, error = alerts.test_connection()
    if ok:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": error})


# ── Dashboard UI ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)
