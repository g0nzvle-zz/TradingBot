from unittest.mock import patch, MagicMock
from data_fetcher import get_news_headlines, get_reddit_sentiment, get_market_context

def test_get_news_returns_list():
    fake_feed = MagicMock()
    fake_feed.entries = [MagicMock(title=f"Headline {i}") for i in range(5)]
    with patch("data_fetcher.feedparser.parse", return_value=fake_feed):
        result = get_news_headlines()
    assert isinstance(result, list)
    assert len(result) <= 10

def test_get_news_returns_strings():
    fake_feed = MagicMock()
    fake_feed.entries = [MagicMock(title="Tech stocks rally")]
    with patch("data_fetcher.feedparser.parse", return_value=fake_feed):
        result = get_news_headlines()
    assert all(isinstance(h, str) for h in result)

def test_reddit_sentiment_returns_dict():
    mock_post = MagicMock()
    mock_post.created_utc = 9999999999.0
    mock_post.title = "NVDA is going up"
    mock_post.selftext = "Great earnings expected"
    mock_subreddit = MagicMock()
    mock_subreddit.search.return_value = [mock_post]
    mock_reddit = MagicMock()
    mock_reddit.subreddit.return_value = mock_subreddit
    with patch("data_fetcher.praw.Reddit", return_value=mock_reddit):
        result = get_reddit_sentiment("NVDA")
    assert "mentions" in result
    assert "sentiment" in result
    assert result["sentiment"] in ("positivo", "neutro", "negativo")

def test_get_market_context_returns_dict():
    with patch("data_fetcher.fetch_ohlcv") as mock_fetch, \
         patch("data_fetcher.calculate_indicators") as mock_ind:
        import pandas as pd
        mock_fetch.return_value = pd.DataFrame({"Close": [100.0]})
        mock_ind.return_value = {"price": 540.0, "rsi": 55.0, "macd_hist": 0.5}
        result = get_market_context()
    assert "spy_price" in result
    assert "vix" in result
