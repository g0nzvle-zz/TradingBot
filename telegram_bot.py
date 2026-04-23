import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str) -> bool:
    """
    Send a Markdown-formatted message to the configured Telegram chat.
    Returns True if the request succeeded (HTTP 200).
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    })
    if response.status_code != 200:
        print(f"Telegram error {response.status_code}: {response.text}")
    return response.status_code == 200
