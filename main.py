from config import (LONG_TERM_TICKERS, SWING_UNIVERSE, SWING_WIN_RATE,
                    SWING_REWARD_RISK, KELLY_FRACTION, MAX_POSITION_PCT, STOP_LOSS_PCT)
from data_fetcher import get_news_headlines, get_market_context, get_ticker_news
from indicators import fetch_ohlcv, calculate_indicators
from screener import run_screener
from kelly import calculate_kelly
from analyzer import build_prompt, build_references, build_swing_fallback, generate_report, GLOSSARY
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
            ind["ticker_news"] = get_ticker_news(ticker)
            long_term_data.append(ind)

    print("3/7 Running stock screener...")
    top_stocks = run_screener(SWING_UNIVERSE)

    print("4/7 Applying Kelly Criterion and fetching ticker news...")
    kelly_pct = calculate_kelly(SWING_WIN_RATE, SWING_REWARD_RISK,
                                KELLY_FRACTION, MAX_POSITION_PCT) * 100
    for stock in top_stocks:
        stock["kelly_pct"] = kelly_pct
        stock["stop_loss"] = stock["price"] * (1 - STOP_LOSS_PCT)
        stock["ticker_news"] = get_ticker_news(stock["ticker"])

    print("5/7 Fetching news headlines...")
    news = get_news_headlines()

    print("6/7 Reading previous recommendations...")
    previous_results = get_previous_results()

    print("7/7 Generating report with LLM and sending to Telegram...")
    prompt = build_prompt(market_ctx, long_term_data, top_stocks, news, previous_results)
    report = generate_report(prompt)

    # Fallback: if the LLM omitted the Swing Trading section, inject it programmatically
    if "⚡ *SWING TRADING" not in report:
        print("  ⚠️ LLM omitted Swing Trading section — injecting programmatic fallback")
        swing_section = build_swing_fallback(top_stocks)
        if "🎯 *GESTIÓN DE RIESGO" in report:
            report = report.replace(
                "🎯 *GESTIÓN DE RIESGO",
                f"{swing_section}\n\n───────────────────────────────────\n🎯 *GESTIÓN DE RIESGO"
            )
        else:
            report = f"{report}\n\n{swing_section}"

    references = build_references(long_term_data, top_stocks, news)
    sections = [report, GLOSSARY]
    if references:
        sections.append(references)
    full_report = "\n\n".join(sections)

    log_recommendations(top_stocks)
    success = send_message(full_report)
    print(f"Report delivered: {success}")


if __name__ == "__main__":
    main()
