
import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. @your_channel

def post_to_telegram(text: str) -> None:
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        raise RuntimeError("TELEGRAM_TOKEN или CHANNEL_ID не заданы в переменных окружения")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, data=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Ошибка Telegram API: {r.status_code} {r.text}")
