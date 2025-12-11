import os
from typing import Optional

import requests


def send_telegram_message(chat_id: str, text: str) -> None:
    token = os.getenv("8476743390:AAGSWkS_F_hU7zqKuYtIuXypckS7YPuVJPw")
    if not token:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=payload, timeout=10)
    except requests.RequestException:
        pass