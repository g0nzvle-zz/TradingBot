import feedparser
import praw
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import (SUBREDDITS, RSS_FEEDS, REDDIT_CLIENT_ID,
                    REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
from indicators import fetch_ohlcv, calculate_indicators


def get_news_headlines() -> list:
    """Fetch top financial news headlines from RSS feeds. Returns up to 10."""
    headlines = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                headlines.append(entry.title)
        except Exception:
            continue
    return headlines[:10]


def get_reddit_sentiment(ticker: str) -> dict:
    """
    Search recent Reddit posts for ticker mentions and analyze sentiment.
    Returns dict with mention count, sentiment label, and positive percentage.
    """
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    analyzer = SentimentIntensityAnalyzer()
    cutoff = datetime.utcnow() - timedelta(hours=48)

    mentions = 0
    scores = []

    for subreddit_name in SUBREDDITS:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.search(ticker, time_filter="week", limit=20):
                post_time = datetime.utcfromtimestamp(post.created_utc)
                if post_time < cutoff:
                    continue
                text = f"{post.title} {post.selftext}"
                if ticker.upper() in text.upper():
                    mentions += 1
                    score = analyzer.polarity_scores(text)["compound"]
                    scores.append(score)
        except Exception:
            continue

    if not scores:
        return {"ticker": ticker, "mentions": 0,
                "sentiment": "neutro", "positive_pct": 0}

    avg = sum(scores) / len(scores)
    positive_pct = int(sum(1 for s in scores if s > 0.05) / len(scores) * 100)
    sentiment = ("positivo" if avg > 0.05
                 else "negativo" if avg < -0.05
                 else "neutro")

    return {
        "ticker": ticker,
        "mentions": mentions,
        "sentiment": sentiment,
        "positive_pct": positive_pct,
    }


def get_market_context() -> dict:
    """Fetch broad market indicators: SPY price/RSI/MACD and VIX level."""
    spy_df = fetch_ohlcv("SPY", period="1mo")
    vix_df = fetch_ohlcv("^VIX", period="5d")

    spy_ind = calculate_indicators(spy_df) if spy_df is not None else {}
    vix_price = float(vix_df["Close"].iloc[-1]) if vix_df is not None else None

    return {
        "spy_price": spy_ind.get("price"),
        "spy_rsi": spy_ind.get("rsi"),
        "spy_macd_hist": spy_ind.get("macd_hist"),
        "vix": vix_price,
    }
