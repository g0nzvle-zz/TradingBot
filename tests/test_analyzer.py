from unittest.mock import patch, MagicMock
from analyzer import build_prompt, generate_report

MARKET_CTX = {
    "spy_price": 540.0, "spy_rsi": 55.0,
    "spy_macd_hist": 0.3, "vix": 18.0,
}

LONG_TERM = [
    {"ticker": "SPY", "price": 540.0, "rsi": 55.0,
     "macd_hist": 0.3, "ema20": 538.0, "ema50": 530.0},
]

TOP_STOCKS = [
    {"ticker": "NVDA", "price": 875.0, "rsi": 52.0, "score": 78,
     "macd_hist": 0.5, "volume": 50_000_000, "volume_sma20": 35_000_000,
     "kelly_pct": 8.0, "stop_loss": 813.75,
     "sentiment": {"sentiment": "positivo", "mentions": 234, "positive_pct": 71}},
]

NEWS = ["NVIDIA expands data center partnerships", "S&P 500 near all-time high"]
PREV = [{"ticker": "AAPL", "fecha": "2026-04-21", "resultado_pct": "+2.3%"}]

def test_build_prompt_returns_string():
    result = build_prompt(MARKET_CTX, LONG_TERM, TOP_STOCKS, NEWS, PREV)
    assert isinstance(result, str)

def test_prompt_contains_ticker():
    result = build_prompt(MARKET_CTX, LONG_TERM, TOP_STOCKS, NEWS, PREV)
    assert "NVDA" in result

def test_prompt_contains_news():
    result = build_prompt(MARKET_CTX, LONG_TERM, TOP_STOCKS, NEWS, PREV)
    assert "NVIDIA" in result

def test_generate_report_calls_groq():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Reporte de prueba"
    mock_client.chat.completions.create.return_value = mock_response
    with patch("analyzer.Groq", return_value=mock_client):
        result = generate_report("prompt de prueba")
    assert result == "Reporte de prueba"
