from config import (LONG_TERM_TICKERS, SWING_UNIVERSE, SWING_WIN_RATE,
                    SWING_REWARD_RISK, KELLY_FRACTION, MAX_POSITION_PCT, STOP_LOSS_PCT)
from data_fetcher import get_reddit_sentiment, get_news_headlines, get_market_context
from indicators import fetch_ohlcv, calculate_indicators
from screener import run_screener
from kelly import calculate_kelly
from analyzer import build_prompt, generate_report
from telegram_bot import send_message
from tracker import log_recommendations, get_previous_results


def main():
    print("1/7 Fetching market context...")
    market_ctx = get_market_context()

    print("2/7 Fetching long-term ETF data...")
    long_term_data = []
    for ticker in LONG_TERM_TICKERS:
        df = fetch_ohlcv(ticker)
        if df is not None:
            ind = calculate_indicators(df)
            ind["ticker"] = ticker
            long_term_data.append(ind)

    print("3/7 Running stock screener...")
    top_stocks = run_screener(SWING_UNIVERSE)

    print("4/7 Fetching Reddit sentiment and applying Kelly Criterion...")
    kelly_pct = calculate_kelly(SWING_WIN_RATE, SWING_REWARD_RISK,
                                KELLY_FRACTION, MAX_POSITION_PCT) * 100
    for stock in top_stocks:
        stock["sentiment"] = get_reddit_sentiment(stock["ticker"])
        stock["kelly_pct"] = kelly_pct
        stock["stop_loss"] = stock["price"] * (1 - STOP_LOSS_PCT)

    print("5/7 Fetching news headlines...")
    news = get_news_headlines()

    print("6/7 Reading previous recommendations...")
    previous_results = get_previous_results()

    print("7/7 Generating report with LLM and sending to Telegram...")
    prompt = build_prompt(market_ctx, long_term_data, top_stocks, news, previous_results)
    report = generate_report(prompt)

    log_recommendations(top_stocks)
    success = send_message(report)
    print(f"Report delivered: {success}")


if __name__ == "__main__":
    main()
