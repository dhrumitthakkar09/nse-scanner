"""
Flask application and all HTTP routes.

Imports shared state from scanner.runner (read-only via _lock) and
config helpers from config.settings to serve and persist settings.
"""

import threading

from flask import Flask, jsonify, render_template_string, request

from config.settings import CONFIG, CREDENTIALS, load_yaml, save_yaml
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
