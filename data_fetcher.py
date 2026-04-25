import feedparser
import requests
import yfinance as yf
from indicators import fetch_ohlcv, calculate_indicators
from config import RSS_FEEDS


def get_news_headlines() -> list:
    """Fetch top financial news headlines from RSS feeds. Returns up to 10 dicts with title and url."""
    results = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                results.append({
                    "title": entry.title,
                    "url": getattr(entry, "link", ""),
                })
        except Exception:
            continue
    return results[:10]


def get_fear_greed_index() -> dict:
    """
    Fetch CNN/Alternative.me Fear & Greed Index (0=extreme fear, 100=extreme greed).
    Returns dict with value (int), label (English), and label_es (Spanish).
    Falls back to neutral (50) on any error.
    """
    labels_es = {
        "Extreme Fear": "Miedo Extremo",
        "Fear": "Miedo",
        "Neutral": "Neutral",
        "Greed": "Codicia",
        "Extreme Greed": "Codicia Extrema",
    }
    try:
        response = requests.get("https://api.alternative.me/fng/", timeout=10)
        data = response.json()["data"][0]
        value = int(data["value"])
        label = data["value_classification"]
        return {"value": value, "label": label, "label_es": labels_es.get(label, label)}
    except Exception:
        return {"value": 50, "label": "Neutral", "label_es": "Neutral"}


def get_ticker_news(ticker: str) -> list:
    """
    Fetch recent news for a specific ticker via yfinance.
    Returns up to 5 dicts with title and url. Handles both old and new yfinance formats.
    """
    try:
        items = yf.Ticker(ticker).news or []
        results = []
        for item in items[:5]:
            title = url = None
            if isinstance(item.get("content"), dict):
                content = item["content"]
                title = content.get("title")
                url = ((content.get("canonicalUrl") or {}).get("url") or
                       (content.get("clickThroughUrl") or {}).get("url"))
            if not title:
                title = item.get("title")
            if not url:
                url = item.get("link", "")
            if title:
                results.append({"title": title, "url": url or ""})
        return results
    except Exception:
        return []


def get_market_context() -> dict:
    """Fetch broad market indicators: SPY price/RSI/MACD, VIX, and Fear & Greed Index."""
    spy_df = fetch_ohlcv("SPY", period="1mo")
    vix_df = fetch_ohlcv("^VIX", period="5d")

    spy_ind = calculate_indicators(spy_df) if spy_df is not None else {}
    vix_price = float(vix_df["Close"].iloc[-1]) if vix_df is not None else None

    fg = get_fear_greed_index()

    return {
        "spy_price": spy_ind.get("price"),
        "spy_rsi": spy_ind.get("rsi"),
        "spy_macd_hist": spy_ind.get("macd_hist"),
        "vix": vix_price,
        "fear_greed_value": fg["value"],
        "fear_greed_label": fg["label_es"],
    }
