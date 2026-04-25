import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

MAX_LENGTH = 4000        # Telegram limit is 4096; leave buffer for safety
SWING_MARKER = "⚡ *SWING TRADING"
GLOSSARY_MARKER = "📚 *GLOSARIO"


def _send_single(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    })
    if response.status_code == 400 and "parse entities" in response.text:
        print("  Markdown parse error — retrying as plain text...")
        response = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        })
    if response.status_code != 200:
        print(f"Telegram error {response.status_code}: {response.text}")
    return response.status_code == 200


def _split_by_length(text: str) -> list:
    """Split text into chunks of MAX_LENGTH at newline boundaries."""
    parts = []
    while text:
        if len(text) <= MAX_LENGTH:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, MAX_LENGTH)
        if split_at == -1:
            split_at = MAX_LENGTH
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts


def send_message(text: str) -> bool:
    """
    Send a Markdown-formatted message to the configured Telegram chat as
    exactly three logical sections:
      1. Resumen general + ETFs (long-term)
      2. Swing Trading
      3. Glosario + Referencias
    Falls back to character splitting if any remaining part still exceeds
    Telegram's 4096-char limit. Returns True only if all parts were delivered.
    """
    markers = [m for m in (SWING_MARKER, GLOSSARY_MARKER) if m in text]

    raw_parts = []
    cursor = 0
    for marker in markers:
        idx = text.find(marker, cursor)
        raw_parts.append(text[cursor:idx].rstrip())
        cursor = idx
    raw_parts.append(text[cursor:])

    final_parts = []
    for raw in raw_parts:
        if not raw:
            continue
        if len(raw) <= MAX_LENGTH:
            final_parts.append(raw)
        else:
            final_parts.extend(_split_by_length(raw))

    success = True
    for i, part in enumerate(final_parts, 1):
        print(f"  Sending part {i}/{len(final_parts)} ({len(part)} chars)...")
        success = _send_single(part) and success
    return success
