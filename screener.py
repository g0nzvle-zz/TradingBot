from indicators import fetch_ohlcv, calculate_indicators
from config import MIN_PRICE, RSI_MIN, RSI_MAX, TOP_N_STOCKS


def score_stock(ind: dict) -> int:
    """
    Score a stock 0-100 based on how many technical signals are aligned.
    Higher = more signals pointing to a buying opportunity.
    """
    score = 0

    # RSI in neutral-to-bullish zone (avoids overbought/oversold extremes)
    if ind.get("rsi") is not None and RSI_MIN < ind["rsi"] < RSI_MAX:
        score += 20

    # MACD line above signal line (bullish momentum)
    if ind.get("macd") is not None and ind.get("macd_signal") is not None:
        if ind["macd"] > ind["macd_signal"]:
            score += 25

    # MACD histogram positive (momentum accelerating upward)
    if ind.get("macd_hist") is not None and ind["macd_hist"] > 0:
        score += 10

    # EMA 20 above EMA 50 (uptrend confirmed)
    if ind.get("ema20") is not None and ind.get("ema50") is not None:
        if ind["ema20"] > ind["ema50"]:
            score += 20

    # Volume above 20-day SMA (move confirmed by market interest)
    if ind.get("volume") is not None and ind.get("volume_sma20") is not None:
        if ind["volume"] > ind["volume_sma20"]:
            score += 15

    # Price below Bollinger Band midline (potential value entry zone)
    if ind.get("price") is not None and ind.get("bb_mid") is not None:
        if ind["price"] < ind["bb_mid"]:
            score += 10

    return score


def run_screener(universe: list) -> list:
    """
    Download data for each ticker, apply filters, rank by score.
    Returns the top TOP_N_STOCKS stocks sorted by score (highest first).
    """
    results = []
    for ticker in universe:
        df = fetch_ohlcv(ticker)
        if df is None or len(df) < 50:
            continue
        ind = calculate_indicators(df)
        ind["ticker"] = ticker

        if ind["price"] is None or ind["price"] < MIN_PRICE:
            continue

        ind["score"] = score_stock(ind)
        results.append(ind)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:TOP_N_STOCKS]
