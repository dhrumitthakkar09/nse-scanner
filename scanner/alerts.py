"""
Telegram alert sender.

Single responsibility: format and dispatch Telegram messages when
new stocks enter the qualified list.
"""

import logging

import requests

from config.settings import CREDENTIALS

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    tok  = CREDENTIALS.get("telegram_bot_token", "")
    chat = CREDENTIALS.get("telegram_chat_id", "")
    return bool(tok and "YOUR_" not in tok and chat and "YOUR_" not in chat)


def send_new_signals(stocks: list[dict], timestamp: str) -> None:
    """
    Send a Telegram MarkdownV2 message for newly qualified stocks.

    Args:
        stocks:    List of stock result dicts (name, sector, price, ath,
                   dist_pct, range_pct, uptrend).
        timestamp: Human-readable IST timestamp string for the message header.
    """
    if not stocks or not is_configured():
        return

    tok  = CREDENTIALS["telegram_bot_token"]
    chat = CREDENTIALS["telegram_chat_id"]

    msg  = f"🔔 *NSE F\\&O Scanner — New Signals*\n_{timestamp}_\n\n"
    msg += f"*{len(stocks)} new stock(s) qualified:*\n\n"
    for s in stocks:
        trend = "▲ Uptrend" if s["uptrend"] else "~ Neutral"
        msg += (
            f"• *{s['name']}*  \\({s['sector']}\\)\n"
            f"  CMP: ₹{s['price']:,.2f}  |  ATH: ₹{s['ath']:,.2f}\n"
            f"  {s['dist_pct']}% from ATH  |  Range: {s['range_pct']}%  |  {trend}\n\n"
        )

    try:
        url  = f"https://api.telegram.org/bot{tok}/sendMessage"
        resp = requests.post(
            url,
            json={"chat_id": chat, "text": msg, "parse_mode": "MarkdownV2"},
            timeout=10,
        )
        if resp.ok:
            logger.info("Telegram alert sent for %d stocks", len(stocks))
        else:
            logger.warning("Telegram error %s: %s", resp.status_code, resp.text[:120])
    except Exception as exc:
        logger.warning("Telegram exception: %s", exc)


def test_connection() -> tuple[bool, str]:
    """
    Send a test message.  Returns (ok, error_message).
    """
    if not is_configured():
        return False, "Telegram not configured — set bot_token and chat_id"

    tok  = CREDENTIALS["telegram_bot_token"]
    chat = CREDENTIALS["telegram_chat_id"]
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            json={"chat_id": chat, "text": "✅ NSE F&O Scanner — Telegram connection test successful!"},
            timeout=10,
        )
        if resp.ok:
            return True, ""
        return False, resp.text[:300]
    except Exception as exc:
        return False, str(exc)
