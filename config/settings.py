"""
Central configuration — scanner parameters, credentials, and constants.

All other modules import CONFIG and CREDENTIALS from here.
Both dicts are mutated at runtime by the settings API so changes
take effect immediately without restarting.
"""

import os
import pytz
import yaml

# ── YAML config file locations (tried in order) ──────────────
_CONFIG_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "..", "..", "dhan", "config.yaml"),
    "D:/PythonProjects/dhan/config.yaml",
]


def load_yaml() -> dict:
    """Load the YAML config from the first candidate path that exists."""
    for path in _CONFIG_CANDIDATES:
        try:
            with open(os.path.normpath(path), encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            continue
    return {}


def save_yaml(cfg: dict) -> bool:
    """Persist cfg to the first writable candidate path. Returns True on success."""
    for path in _CONFIG_CANDIDATES:
        try:
            with open(os.path.normpath(path), "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception:
            continue
    return False


def get_yaml_path() -> str:
    """Return the path of the first existing config file, or the last candidate."""
    for path in _CONFIG_CANDIDATES:
        if os.path.exists(os.path.normpath(path)):
            return os.path.normpath(path)
    return os.path.normpath(_CONFIG_CANDIDATES[-1])


# ── Load once on import ───────────────────────────────────────
_yaml = load_yaml()

# ── Scanner parameters (mutated at runtime via settings API) ──
CONFIG: dict = {
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
    "api_call_delay_secs":    0.4,
}

# ── Credentials (mutated at runtime via settings API) ─────────
# Using a single mutable dict avoids `global` keyword across modules.
CREDENTIALS: dict = {
    "dhan_client_id":     str(_yaml.get("dhan", {}).get("client_id", "")),
    "dhan_access_token":  str(_yaml.get("dhan", {}).get("access_token", "")),
    "telegram_bot_token": str(_yaml.get("telegram", {}).get("bot_token", "")),
    "telegram_chat_id":   str(_yaml.get("telegram", {}).get("chat_id", "")),
}

# ── Constants ─────────────────────────────────────────────────
IST          = pytz.timezone("Asia/Kolkata")
MARKET_OPEN  = (9, 15)
MARKET_CLOSE = (15, 30)

DHAN_BASE        = "https://api.dhan.co/v2"
SCRIP_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
