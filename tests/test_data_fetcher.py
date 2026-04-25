from unittest.mock import patch, MagicMock
from data_fetcher import get_news_headlines, get_fear_greed_index, get_market_context, get_ticker_news


def test_get_news_returns_list():
    fake_feed = MagicMock()
    fake_feed.entries = [MagicMock(title=f"Headline {i}", link=f"https://example.com/{i}") for i in range(5)]
    with patch("data_fetcher.feedparser.parse", return_value=fake_feed):
        result = get_news_headlines()
    assert isinstance(result, list)
    assert len(result) <= 10


def test_get_news_returns_dicts_with_title_and_url():
    fake_feed = MagicMock()
    fake_feed.entries = [MagicMock(title="Tech stocks rally", link="https://example.com/news")]
    with patch("data_fetcher.feedparser.parse", return_value=fake_feed):
        result = get_news_headlines()
    assert all(isinstance(h, dict) for h in result)
    assert all("title" in h and "url" in h for h in result)
    assert result[0]["title"] == "Tech stocks rally"


def test_get_fear_greed_returns_dict():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"value": "30", "value_classification": "Fear"}]
    }
    with patch("data_fetcher.requests.get", return_value=mock_response):
        result = get_fear_greed_index()
    assert "value" in result
    assert "label_es" in result
    assert isinstance(result["value"], int)
    assert result["value"] == 30
    assert result["label_es"] == "Miedo"


def test_get_fear_greed_fallback_on_error():
    with patch("data_fetcher.requests.get", side_effect=Exception("timeout")):
        result = get_fear_greed_index()
    assert result["value"] == 50
    assert result["label_es"] == "Neutral"


def test_get_ticker_news_returns_list_of_dicts():
    mock_ticker = MagicMock()
    mock_ticker.news = [
        {"title": "Adobe faces AI competition", "link": "https://example.com/1"},
        {"content": {"title": "Palantir drops on earnings",
                     "canonicalUrl": {"url": "https://example.com/2"}}},
    ]
    with patch("data_fetcher.yf.Ticker", return_value=mock_ticker):
        result = get_ticker_news("ADBE")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "Adobe faces AI competition"
    assert result[0]["url"] == "https://example.com/1"
    assert result[1]["title"] == "Palantir drops on earnings"
    assert result[1]["url"] == "https://example.com/2"


def test_get_ticker_news_fallback_on_error():
    with patch("data_fetcher.yf.Ticker", side_effect=Exception("network error")):
        result = get_ticker_news("AAPL")
    assert result == []


def test_get_market_context_returns_dict():
    mock_fg = {"value": 45, "label": "Fear", "label_es": "Miedo"}
    with patch("data_fetcher.fetch_ohlcv") as mock_fetch, \
         patch("data_fetcher.calculate_indicators") as mock_ind, \
         patch("data_fetcher.get_fear_greed_index", return_value=mock_fg):
        import pandas as pd
        mock_fetch.return_value = pd.DataFrame({"Close": [100.0]})
        mock_ind.return_value = {"price": 540.0, "rsi": 55.0, "macd_hist": 0.5}
        result = get_market_context()
    assert "spy_price" in result
    assert "vix" in result
    assert "fear_greed_value" in result
    assert "fear_greed_label" in result
