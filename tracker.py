import csv
import os
from datetime import date
from config import TRACKER_FILE

FIELDS = ["fecha", "ticker", "precio_entrada", "accion",
          "kelly_sugerido", "precio_actual", "resultado_pct"]


def log_recommendations(recommendations: list) -> None:
    """Append today's top picks to the CSV tracker."""
    file_exists = os.path.exists(TRACKER_FILE)
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        for rec in recommendations:
            writer.writerow({
                "fecha": date.today().isoformat(),
                "ticker": rec["ticker"],
                "precio_entrada": f"{rec['price']:.2f}",
                "accion": "COMPRA",
                "kelly_sugerido": f"{rec['kelly_pct']:.0f}%",
                "precio_actual": "",
                "resultado_pct": "",
            })


def get_previous_results() -> list:
    """
    Read tracker CSV, update prices for open recommendations,
    and return only entries that have a resultado_pct.
    CSV is written back if any prices were updated.
    """
    if not os.path.exists(TRACKER_FILE):
        return []

    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    updated = []
    changed = False

    for row in rows:
        if row["resultado_pct"] == "" and row["precio_entrada"]:
            try:
                import yfinance as yf
                ticker = row["ticker"]
                entry_price = float(row["precio_entrada"])
                current = float(yf.Ticker(ticker).fast_info["lastPrice"])
                result_pct = (current - entry_price) / entry_price * 100
                row["precio_actual"] = f"{current:.2f}"
                row["resultado_pct"] = f"{result_pct:+.1f}%"
                changed = True
            except Exception:
                pass
        updated.append(row)

    if changed:
        with open(TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(updated)

    return [r for r in updated if r["resultado_pct"]]
